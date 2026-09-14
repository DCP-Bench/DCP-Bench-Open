"""Compatibility loader for trusted dataset scripts; never executes their solve tail."""
import ast
import contextlib
import copy
import multiprocessing as mp
import os

from .results import EvaluationError, canonical


def parse_source(source):
    tree = ast.parse(source)
    starts = [i for i, line in enumerate(source.splitlines(), 1)
              if line.strip().lower() == "# data"]
    ends = [i for i, line in enumerate(source.splitlines(), 1)
            if line.strip().lower() == "# end of data"]
    if len(starts) != len(ends) or len(starts) > 1 or (starts and starts[0] >= ends[0]):
        raise EvaluationError("reference_error", "Unrecognized data section")
    data_nodes = [n for n in tree.body if starts and starts[0] < n.lineno < ends[0]]
    solve_nodes = []
    for i, node in enumerate(tree.body):
        calls = [n for n in ast.walk(node) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Attribute) and n.func.attr in ("solve", "solveAll")]
        if calls:
            if (len(calls) != 1 or not isinstance(calls[0].func.value, ast.Name)
                    or calls[0].func.value.id != "model"
                    or not isinstance(node, (ast.Expr, ast.If))):
                raise EvaluationError("reference_error", "Unsupported solve pattern")
            solve_nodes.append(i)
    if len(solve_nodes) != 1:
        raise EvaluationError("reference_error", "Expected exactly one model solve section")
    cut = solve_nodes[0]
    outputs = [n.value for node in tree.body[cut:] for n in ast.walk(node)
               if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "solution" for t in n.targets)]
    if len(outputs) != 1 or not isinstance(outputs[0], ast.Dict):
        raise EvaluationError("reference_error", "Expected a literal solution dictionary")
    if any(not isinstance(k, ast.Constant) or not isinstance(k.value, str) for k in outputs[0].keys):
        raise EvaluationError("reference_error", "Output keys must be literal strings")
    keys = [k.value for k in outputs[0].keys]
    if not keys or len(set(keys)) != len(keys):
        raise EvaluationError("reference_error", "Empty or duplicate declared outputs")
    return tree, data_nodes, cut, outputs[0]


def embedded_instance(source):
    _, data, _, _ = parse_source(source)
    namespace = {}
    try:
        exec(compile(ast.Module(body=data, type_ignores=[]), "<reference-data>", "exec"), namespace)
    except Exception as error:
        raise EvaluationError("reference_error", f"Cannot load embedded data: {error}") from error
    return {k: v for k, v in namespace.items() if not k.startswith("__")}


def available_instances(source, instances):
    """Every distinct instance: the embedded example first, then unseen records."""
    expected = embedded_instance(source)
    available = [("example", expected)]
    seen = {canonical(available[0][1])}
    if not isinstance(instances, list) or any(not isinstance(x, dict) for x in instances):
        raise EvaluationError("reference_error", "Instance file must contain a list of objects")
    for i, instance in enumerate(instances):
        missing = set(expected) - set(instance)
        if missing:
            raise EvaluationError("reference_error", f"Instance is missing fields: {sorted(missing)}")
        # Names and notes do not make a new mathematical instance. Keep the
        # first record intact for execution, but compare only declared inputs.
        key = canonical({name: instance[name] for name in expected})
        if key not in seen:
            available.append((f"json:{i}", instance))
            seen.add(key)
    return available


def choose_instances(available, count=1, ids=None):
    if ids is not None:
        if not ids or len(set(ids)) != len(ids):
            raise EvaluationError("invalid_request", "Instance IDs must be nonempty and unique")
        by_id = dict(available)
        # A named instance that does not exist is a mistake, not a budget.
        if any(x not in by_id for x in ids):
            raise EvaluationError("invalid_request", f"Available distinct instances: {list(by_id)}")
        return [(x, by_id[x]) for x in ids]
    if type(count) is not int or count < 1:
        raise EvaluationError("invalid_request", "instance_count must be a positive integer")
    # A count is a coverage budget, not a requirement: a problem with fewer
    # distinct instances than requested is covered in full by all of them.
    return available[:count]


def select_instances(source, instances, count=1, ids=None):
    return choose_instances(available_instances(source, instances), count, ids)


class OutputExpressions(ast.NodeTransformer):
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in ("int", "bool") and len(node.args) == 1:
            return self.visit(node.args[0])
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ("value", "tolist", "astype"):
                return self.visit(node.func.value)
            if (node.func.attr == "objective_value" and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "model"):
                return ast.copy_location(ast.Attribute(value=ast.Name(id="model", ctx=ast.Load()),
                                                      attr="objective_", ctx=ast.Load()), node)
        raise EvaluationError("reference_error", f"Unsupported output expression: {ast.unparse(node)}")


def load_reference(source, instance):
    import cpmpy as cp
    tree, data, cut, output = parse_source(source)
    expected = embedded_instance(source)
    # All declared data fields must be present. Extra keys are metadata (e.g.
    # names/notes on csplib instance lists) and are ignored by the reference.
    missing = set(expected) - set(instance)
    if missing:
        raise EvaluationError("reference_error", f"Instance is missing fields: {sorted(missing)}")
    namespace = dict(instance)
    body = [n for n in tree.body[:cut] if n not in data]
    # Reference source is trusted. Candidate source is never loaded in this process.
    exec(compile(ast.Module(body=body, type_ignores=[]), "<reference>", "exec"), namespace)
    model = namespace.get("model")
    if not isinstance(model, cp.Model):
        raise EvaluationError("reference_error", "Reference does not construct a CPMpy Model")
    expr = OutputExpressions().visit(copy.deepcopy(output))
    expressions = eval(compile(ast.fix_missing_locations(ast.Expression(expr)), "<outputs>", "eval"), namespace)
    return model, expressions


def sequence(value):
    import numpy as np
    return isinstance(value, (list, tuple, np.ndarray)) and not (isinstance(value, np.ndarray) and value.ndim == 0)


def bind_output(expression, value, label):
    import numpy as np
    if sequence(expression):
        if not isinstance(value, list) or len(expression) != len(value):
            raise EvaluationError("invalid_output", f"Wrong shape at {label}")
        result = []
        normalized = []
        for i, (e, v) in enumerate(zip(expression, value)):
            constraints, item = bind_output(e, v, f"{label}[{i}]")
            result.extend(constraints)
            normalized.append(item)
        return result, normalized
    boolean = isinstance(expression, (bool, np.bool_)) or (hasattr(expression, "is_bool") and expression.is_bool())
    if boolean:
        if type(value) not in (bool, int) or value not in (0, 1):
            raise EvaluationError("invalid_output", f"Expected Boolean or 0/1 at {label}")
        value = bool(value)
    elif type(value) is not int:
        raise EvaluationError("invalid_output", f"Expected integer at {label}")
    elif not -(2**63) < value < 2**63:
        raise EvaluationError("invalid_output", f"Integer outside supported solver range at {label}")
    return [expression == value], value


class Reference:
    def __init__(self, source, instance, timeout):
        from cpmpy.solvers.solver_interface import ExitStatus
        self.model, self.outputs = load_reference(source, instance)
        self.timeout = timeout
        self.optimum = None
        self.model.solve(solver="ortools", time_limit=timeout, num_search_workers=1)
        status = self.model.status().exitstatus
        if status == ExitStatus.UNSATISFIABLE:
            raise EvaluationError("unsupported_unsat", "Reference is UNSAT")
        if status not in (ExitStatus.FEASIBLE, ExitStatus.OPTIMAL):
            raise EvaluationError("reference_timeout", "Reference feasibility was not established")
        if self.model.has_objective():
            if status != ExitStatus.OPTIMAL:
                raise EvaluationError("reference_timeout", "Reference optimum was not proven")
            self.optimum = int(self.model.objective_value())

    def check(self, solution):
        import cpmpy as cp
        from cpmpy.solvers.solver_interface import ExitStatus
        if not isinstance(solution, dict) or not solution or set(solution) != set(self.outputs):
            raise EvaluationError("invalid_output", f"Expected exactly these outputs: {sorted(self.outputs)}")
        constraints, normalized = [], {}
        for key, expr in self.outputs.items():
            new, normalized[key] = bind_output(expr, solution[key], key)
            constraints.extend(new)

        def feasible(extra):
            test = cp.Model(self.model.constraints + constraints + extra)
            ok = test.solve(solver="ortools", time_limit=self.timeout, num_search_workers=1)
            if not ok and test.status().exitstatus != ExitStatus.UNSATISFIABLE:
                raise EvaluationError("reference_timeout", "Reference assignment check did not finish")
            return ok

        if not feasible([]):
            raise EvaluationError("invalid_solution", "Declared outputs cannot extend to a reference solution")
        if self.optimum is not None and not feasible([self.model.objective_ == self.optimum]):
            raise EvaluationError("suboptimal_solution", "Declared outputs cannot achieve the reference optimum")
        return normalized


def _worker(connection, source, instance, timeout):
    try:
        with open(os.devnull, "w") as quiet, contextlib.redirect_stdout(quiet):
            ref = Reference(source, instance, timeout)
            connection.send({"ok": True, "outputs": list(ref.outputs), "is_optimization": ref.model.has_objective(),
                             "optimum": ref.optimum})
            while True:
                solution = connection.recv()
                try:
                    connection.send({"ok": True, "normalized": ref.check(solution)})
                except EvaluationError as e:
                    connection.send({"ok": False, "reason": e.reason, "detail": e.detail})
    except (EOFError, BrokenPipeError):
        pass
    except Exception as e:
        connection.send({"ok": False, "reason": getattr(e, "reason", "reference_error"), "detail": str(e)})
    finally:
        connection.close()


class ReferenceSession:
    """Bound model building and checks in a separate, killable trusted process."""
    def __init__(self, source, instance, timeout):
        self.timeout = timeout
        ctx = mp.get_context("spawn")
        self.pipe, child = ctx.Pipe()
        self.process = ctx.Process(target=_worker, args=(child, source, instance, timeout), daemon=True)
        self.process.start()
        child.close()
        try:
            self.metadata = self.receive()
        except Exception:
            self.close()
            raise

    def receive(self):
        if not self.pipe.poll(self.timeout):
            raise EvaluationError("reference_timeout", "Reference operation exceeded its wall-clock limit")
        try:
            result = self.pipe.recv()
        except EOFError as e:
            raise EvaluationError("reference_error", "Reference process exited unexpectedly") from e
        if not result["ok"]:
            raise EvaluationError(result["reason"], result["detail"])
        return result

    def check(self, solution):
        self.pipe.send(solution)
        return self.receive()["normalized"]

    def close(self):
        self.pipe.close()
        if self.process.is_alive():
            self.process.terminate()
        self.process.join(5)
        if self.process.is_alive():
            self.process.kill()
            self.process.join()
