"""Runner protocol for the gurobipy_python integration. Runs inside the image only.

A submission defines `build(instance)` returning `(model, outputs)`, where
`model` is a `gurobipy.Model`. Its own objective says whether this is an
optimization: an objective with no terms is a satisfaction problem, and
`ModelSense` gives the direction, so the submission needs no extra convention.

Four things about Gurobi shape this runner.

Gurobi reports OPTIMAL once the incumbent is within `MIPGap` of the bound, and
the default gap is 1e-4 relative: on an objective near 20000 that leaves room for
a solution 2 away from the optimum. The runner sets `MIPGap` to 0, so OPTIMAL
means proven, whatever the submission set.

Integer variables come back within `IntFeasTol` (1e-5) of an integer rather than
on it. The runner rounds every integer variable and evaluates declared
expressions over the rounded values, so a declared output is what the integers
say; a continuous variable must itself be integral within 1e-6.

The licence bundled with the gurobipy wheel refuses a model above 2000 variables
or 2000 linear constraints. That is reported as `unsupported` with the model's
size, never as a timeout or as a fault in the model.

Gurobi returns one solution rather than a stream, so enumeration pins the
objective to the proven optimum and adds a no-good over the integer variables
the declared outputs are built from: a linear one for binaries, and indicator
constraints for general integers, which need no bound.

Gurobi's library prints its licence banner from C, below Python's `sys.stdout`,
so the protocol stream keeps file descriptor 1 to itself and everything else
written to stdout goes to stderr.
"""
import contextlib
import importlib.util
import json
import numbers
import os
from pathlib import Path
import signal
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish  # noqa: E402

import gurobipy as gp  # noqa: E402
from gurobipy import GRB  # noqa: E402

INPUT = Path("/input")
# A declared output has to be an integer; a continuous value further from one
# than this is a modelling error rather than solver noise.
TOLERANCE = 1e-6
STATUS_NAMES = {getattr(GRB.Status, name): name for name in dir(GRB.Status) if name.isupper()}


def protocol_stream():
    """Give the JSONL protocol its own copy of fd 1 and send fd 1 to stderr."""
    protocol = os.dup(1)
    os.dup2(2, 1)
    sys.stdout = os.fdopen(protocol, "w", buffering=1)


def expanded(value):
    """Matrix variables and NumPy arrays as nested lists of their elements."""
    if isinstance(value, (gp.Var, gp.LinExpr, gp.QuadExpr, bool, numbers.Number)):
        return value
    if hasattr(value, "tolist"):
        return value.tolist()
    return value


def leaves(value):
    """Every declared output value, with gurobipy's expressions left whole."""
    value = expanded(value)
    if isinstance(value, dict):
        return [x for v in value.values() for x in leaves(v)]
    if isinstance(value, (list, tuple)):
        return [x for v in value for x in leaves(v)]
    return [value]


def resolved(value, read_one):
    """The declared outputs with every leaf replaced by its integer value."""
    value = expanded(value)
    if isinstance(value, dict):
        return {k: resolved(v, read_one) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [resolved(v, read_one) for v in value]
    return read_one(value)


def terms(expression):
    """The variables of a linear or quadratic expression, in no particular order."""
    if isinstance(expression, gp.Var):
        return [expression]
    if isinstance(expression, gp.LinExpr):
        return [expression.getVar(i) for i in range(expression.size())]
    if isinstance(expression, gp.QuadExpr):
        found = terms(expression.getLinExpr())
        for i in range(expression.size()):
            found += [expression.getVar1(i), expression.getVar2(i)]
        return found
    return []


def integer(variable):
    return variable.VType in (GRB.BINARY, GRB.INTEGER)


def variable_value(variable):
    """An integer variable rounded to the integer its tolerance allows."""
    value = variable.X
    return round(value) if integer(variable) else value


def expression_value(expression):
    if isinstance(expression, gp.Var):
        return variable_value(expression)
    if isinstance(expression, gp.LinExpr):
        return expression.getConstant() + sum(
            expression.getCoeff(i) * variable_value(expression.getVar(i))
            for i in range(expression.size()))
    if isinstance(expression, gp.QuadExpr):
        return expression_value(expression.getLinExpr()) + sum(
            expression.getCoeff(i) * variable_value(expression.getVar1(i))
            * variable_value(expression.getVar2(i)) for i in range(expression.size()))
    raise ValueError(f"Unsupported declared output of type {type(expression).__name__}")


def integral(expression):
    """Whether the expression can only take integer values."""
    if isinstance(expression, gp.Var):
        return integer(expression)
    if isinstance(expression, gp.LinExpr):
        coefficients = [expression.getConstant()] + [expression.getCoeff(i) for i in range(expression.size())]
    elif isinstance(expression, gp.QuadExpr):
        linear = expression.getLinExpr()
        coefficients = ([linear.getConstant()] + [linear.getCoeff(i) for i in range(linear.size())]
                        + [expression.getCoeff(i) for i in range(expression.size())])
    else:
        return False
    return all(float(c).is_integer() for c in coefficients) and all(integer(v) for v in terms(expression))


def read(value):
    """One declared output value: an integer, never a float from the solver."""
    if isinstance(value, bool):
        return value
    if isinstance(value, numbers.Integral):
        return int(value)
    if isinstance(value, numbers.Real):
        number = value
    else:
        number = expression_value(value)
    rounded = round(number)
    if abs(number - rounded) > TOLERANCE:
        raise ValueError("Declared outputs must be integer valued; no coercion from "
                         f"fractional values (got {number})")
    return int(rounded)


def load(instance):
    spec = importlib.util.spec_from_file_location("candidate", str(INPUT / "model.py"))
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        returned = module.build(instance)
    if not isinstance(returned, tuple) or len(returned) != 2:
        raise ValueError("build(instance) must return (model, outputs)")
    model, outputs = returned
    if not isinstance(model, gp.Model):
        raise ValueError("build(instance) must return a gurobipy.Model")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return a nonempty output dictionary")
    return model, outputs


def cut_variables(outputs):
    """The variables a no-good has to move, each once."""
    collected = {}
    for leaf in leaves(outputs):
        for variable in terms(leaf):
            collected[variable.index] = variable
    return list(collected.values())


def forbid(model, variables, index):
    """Forbid the assignment the variables currently hold."""
    differs = []
    for position, variable in enumerate(variables):
        value = variable_value(variable)
        low, high = variable.LB, variable.UB
        if low == high:
            continue
        if low >= 0 and high <= 1:
            # A binary differs from its value through a linear term alone.
            differs.append(variable if value == 0 else 1 - variable)
            continue
        if value > low:
            below = model.addVar(vtype=GRB.BINARY, name=f"_below_{index}_{position}")
            model.addGenConstrIndicator(below, True, variable, GRB.LESS_EQUAL, value - 1)
            differs.append(below)
        if value < high:
            above = model.addVar(vtype=GRB.BINARY, name=f"_above_{index}_{position}")
            model.addGenConstrIndicator(above, True, variable, GRB.GREATER_EQUAL, value + 1)
            differs.append(above)
    if not differs:
        # Every declared variable is pinned to its only value: nothing else exists.
        return False
    model.addConstr(gp.quicksum(differs) >= 1, name=f"_nogood_{index}")
    return True


def pin(model, objective):
    """Keep only assignments at the proven optimum, then search for any of them."""
    best = expression_value(objective)
    if integral(objective):
        best = round(best)
        low, high = best - 0.5, best + 0.5
    else:
        slack = TOLERANCE * max(1.0, abs(best))
        low, high = best - slack, best + slack
    if isinstance(objective, gp.QuadExpr):
        model.addQConstr(objective >= low, name="_optimum_low")
        model.addQConstr(objective <= high, name="_optimum_high")
    else:
        model.addLConstr(objective, GRB.GREATER_EQUAL, low, name="_optimum_low")
        model.addLConstr(objective, GRB.LESS_EQUAL, high, name="_optimum_high")
    model.setObjective(0)


def attempt(model, deadline):
    """Solve once inside the remaining budget; say what Gurobi actually concluded."""
    left = deadline - time.monotonic()
    if left <= 0:
        return "timeout"
    model.Params.TimeLimit = left
    with contextlib.redirect_stdout(sys.stderr):
        model.optimize()
    if model.Status == GRB.INF_OR_UNBD:
        # Presolve stopped before telling the two apart; without dual reductions it has to.
        left = deadline - time.monotonic()
        if left <= 0:
            return "timeout"
        model.Params.DualReductions = 0
        model.Params.TimeLimit = left
        with contextlib.redirect_stdout(sys.stderr):
            model.optimize()
    status = model.Status
    if status == GRB.OPTIMAL and model.SolCount > 0:
        return "solved"
    if status == GRB.INFEASIBLE:
        return "infeasible"
    if status == GRB.UNBOUNDED:
        return "unbounded"
    if status == GRB.TIME_LIMIT:
        return "timeout"
    return STATUS_NAMES.get(status, f"status {status}")


def configure(model):
    """The settings that decide what a verdict means; they override the submission's."""
    model.Params.OutputFlag = 0
    model.Params.Threads = 1
    model.Params.MIPGap = 0


def objective_of(model):
    """The single objective, or None for a satisfaction problem."""
    if model.NumObj > 1:
        raise NotImplementedError("Only a single objective is supported")
    objective = model.getObjective()
    if isinstance(objective, gp.QuadExpr):
        empty = objective.size() == 0 and objective.getLinExpr().size() == 0
    else:
        empty = objective.size() == 0
    return None if empty else objective


def solve(request):
    deadline = time.monotonic() + request["execution_timeout"]
    model, outputs = load(request["instance"])
    with contextlib.redirect_stdout(sys.stderr):
        configure(model)
        model.update()
    objective = objective_of(model)
    variables = cut_variables(outputs)

    verdict = attempt(model, deadline)
    if verdict == "infeasible":
        return finish("unsat")
    if verdict == "unbounded":
        return finish("error", "The objective is unbounded")
    if verdict == "timeout":
        return finish("timeout", "Candidate optimum was not proven" if objective is not None else "")
    if verdict != "solved":
        return finish("error", f"Gurobi stopped with status {verdict}")

    limit = request["solution_limit"]
    if limit > 1:
        continuous = [v.VarName for v in variables if not integer(v)]
        if continuous:
            return finish("unsupported", "Enumeration needs integer declared outputs; "
                                         f"{continuous[0]} is continuous")

    seen, count, index = set(), 0, 0
    while True:
        values = resolved(outputs, read)
        key = json.dumps(values, sort_keys=True)
        if key not in seen:
            seen.add(key)
            emit({"type": "solution", "values": values})
            count += 1
            if count >= limit:
                return finish("limit")
        if objective is not None:
            # Only assignments that achieve the proven optimum may be enumerated.
            pin(model, objective)
            objective = None
        if not forbid(model, variables, index):
            return finish("complete")
        index += 1
        verdict = attempt(model, deadline)
        if verdict == "infeasible":
            return finish("complete")
        if verdict == "timeout":
            return finish("timeout")
        if verdict != "solved":
            return finish("error", f"Gurobi stopped with status {verdict}")


def main():
    protocol_stream()
    try:
        request = json.loads((INPUT / "request.json").read_text())
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by gurobipy_python")

        def expired(signum, frame):
            raise TimeoutError("Runner execution budget exceeded")

        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, request["execution_timeout"] + 5)
        solve(request)
    except TimeoutError:
        finish("timeout")
    except gp.GurobiError as error:
        if error.errno == GRB.Error.SIZE_LIMIT_EXCEEDED:
            finish("unsupported", "The model is larger than the size-limited licence bundled with "
                                  f"gurobipy allows (2000 variables, 2000 linear constraints): {error}")
        else:
            import traceback
            traceback.print_exc(file=sys.stderr)
            finish("error", f"Gurobi error {error.errno}: {error}")
    except NotImplementedError as error:
        finish("unsupported", str(error))
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))


if __name__ == "__main__":
    main()
