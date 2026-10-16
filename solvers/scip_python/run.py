"""Runner protocol for the scip_python integration. Runs inside the image only.

A submission defines `build(instance)` returning `(model, outputs)`, where
`model` is a `pyscipopt.Model` and `outputs` maps declared names to variables or
linear expressions. The objective is whatever the submission set with
`setObjective`; an objective with no variable terms is a satisfaction problem.

Five things about SCIP shape this runner.

SCIP stops at a gap of `limits/gap` and `limits/absgap`. The runner sets both to
0 after `build` returns, so `optimal` means proven whatever the submission set.

SCIP reports values as floats within its feasibility tolerance. The runner rounds
every integer declared output, and a continuous declared value must itself be
integral within 1e-6.

With no incumbent, `getVal` silently returns 0. The runner reads a value only
after the status is `optimal` and `getBestSol()` is not None.

SCIP can crash the whole process (SIGSEGV), for example on an indicator
constraint without an explicit binary. So the model runs in a worker process.
The supervisor relays the worker's solution records, holds back its final
status, and reports a worker that dies without one as `error`, naming the signal.
The supervisor also enforces the execution budget, reporting a worker it had to
kill as `timeout`.

SCIP returns one solution at a time. Enumeration fixes the objective to the
proven optimum, then adds a no-good over the variables the declared outputs are
built from: a linear one for binaries, and indicator constraints with explicit
binary selectors for general integers. Solutions are deduplicated on the declared
outputs, so auxiliary variables never produce repeats.
"""
import contextlib
import importlib.util
import json
import numbers
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish  # noqa: E402

INPUT = Path("/input")
# A declared integer value further from an integer than this is a modelling
# error rather than solver noise.
TOLERANCE = 1e-6
# Seconds the supervisor allows the worker beyond the execution budget before it
# kills the worker: start-up and build time count against the same budget.
GRACE = 5


def supervise():
    """Run the worker, relay its solutions, and decide the single final status."""
    request = json.loads((INPUT / "request.json").read_text())
    if request.get("legacy"):
        return finish("unsupported", "Legacy submissions are not supported by scip_python")
    worker = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--worker"],
                              stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, text=True, bufsize=1)
    expired = threading.Event()

    def kill():
        expired.set()
        worker.kill()

    watchdog = threading.Timer(request["execution_timeout"] + GRACE, kill)
    watchdog.start()
    final = None
    try:
        for line in worker.stdout:
            try:
                record = json.loads(line)
            except ValueError:
                # A line cut short by a kill; the missing final status reports it.
                continue
            if record.get("type") == "status":
                final = line
            else:
                sys.stdout.write(line)
                sys.stdout.flush()
    finally:
        code = worker.wait()
        watchdog.cancel()

    if final is not None and code == 0:
        sys.stdout.write(final)
        sys.stdout.flush()
    elif expired.is_set():
        finish("timeout", "Candidate did not finish within its execution budget")
    elif code < 0:
        finish("error", f"SCIP worker terminated by signal {signal.Signals(-code).name}")
    elif code != 0:
        finish("error", f"SCIP worker exited with status {code}" + ("" if final is None else
                                                                   " after its final status"))
    else:
        finish("error", "SCIP worker exited without a final status")


def protocol_stream():
    """Give the JSONL protocol its own copy of fd 1 and send fd 1 to stderr."""
    protocol = os.dup(1)
    os.dup2(2, 1)
    sys.stdout = os.fdopen(protocol, "w", buffering=1)


def load(instance):
    from pyscipopt import Model
    spec = importlib.util.spec_from_file_location("candidate", str(INPUT / "model.py"))
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        returned = module.build(instance)
    if not isinstance(returned, tuple) or len(returned) != 2:
        raise ValueError("build(instance) must return (model, outputs)")
    model, outputs = returned
    if not isinstance(model, Model):
        raise ValueError("build(instance) must return a pyscipopt.Model")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return a nonempty output dictionary")
    return model, outputs


def leaves(value):
    """Every declared output value, with expressions and variables left whole."""
    if isinstance(value, dict):
        return [x for v in value.values() for x in leaves(v)]
    if isinstance(value, (list, tuple)):
        return [x for v in value for x in leaves(v)]
    if hasattr(value, "tolist") and not hasattr(value, "terms") and not hasattr(value, "vtype"):
        return leaves(value.tolist())
    return [value]


def resolved(value, read_one):
    """The declared outputs with every leaf replaced by read_one(leaf)."""
    if isinstance(value, dict):
        return {k: resolved(v, read_one) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [resolved(v, read_one) for v in value]
    if hasattr(value, "tolist") and not hasattr(value, "terms") and not hasattr(value, "vtype"):
        return resolved(value.tolist(), read_one)
    return read_one(value)


def variables_of(outputs):
    """The distinct variables the declared outputs are built from, in order."""
    from pyscipopt import Expr
    found = {}
    for leaf in leaves(outputs):
        if hasattr(leaf, "vtype"):
            found.setdefault(leaf.getIndex(), leaf)
        elif isinstance(leaf, Expr):
            for term in leaf.terms:
                for variable in term:
                    found.setdefault(variable.getIndex(), variable)
    return list(found.values())


def read(number):
    """One declared output value: an integer, never a float from the solver."""
    if isinstance(number, bool):
        return number
    rounded = round(number)
    if abs(number - rounded) > TOLERANCE:
        raise ValueError("Declared outputs must be integer valued; no coercion from "
                         f"fractional values (got {number})")
    return int(rounded)


def number_in(solution, value):
    """The number a declared leaf takes in the solution."""
    if isinstance(value, numbers.Real):
        return float(value)
    return solution[value]


def configure(model):
    """Settings that decide what a verdict means; they override the submission's."""
    model.hideOutput()
    model.setIntParam("parallel/maxnthreads", 1)
    model.setParam("limits/gap", 0)
    model.setParam("limits/absgap", 0)


def objective_of(model):
    """The objective expression, or None for a satisfaction problem."""
    objective = model.getObjective()
    if all(coefficient == 0 for term, coefficient in objective.terms.items() if len(term) > 0):
        return None
    return objective


def integral_objective(objective):
    """Whether every term of the objective takes integer values only."""
    for term, coefficient in objective.terms.items():
        if not float(coefficient).is_integer():
            return False
        if any(variable.vtype() == "CONTINUOUS" for variable in term):
            return False
    return True


def attempt(model, deadline):
    """Solve once inside the remaining budget; say what SCIP actually concluded."""
    left = deadline - time.monotonic()
    if left <= 0:
        return "timelimit"
    model.setParam("limits/time", left)
    model.optimize()
    status = model.getStatus()
    if status == "inforunbd":
        # Presolve stopped before telling infeasible from unbounded; without it SCIP can.
        left = deadline - time.monotonic()
        if left <= 0:
            return "timelimit"
        from pyscipopt import SCIP_PARAMSETTING
        model.freeTransform()
        model.setPresolve(SCIP_PARAMSETTING.OFF)
        model.setParam("limits/time", left)
        model.optimize()
        status = model.getStatus()
    if status == "optimal" and model.getBestSol() is not None:
        return "solved"
    return status


def pin(model, objective, best, integral):
    """Keep only assignments at the proven optimum, then search for any of them."""
    if integral:
        low, high = round(best) - 0.5, round(best) + 0.5
    else:
        slack = TOLERANCE * max(1.0, abs(best))
        low, high = best - slack, best + slack
    model.addCons(objective >= low)
    model.addCons(objective <= high)
    model.setObjective(0, "minimize")


def snapshot(model, outputs, variables, objective):
    """Read everything a later step needs before a solution is released.

    Solutions are invalid once the transformed problem is freed, so the values
    the no-goods and the objective pin need are copied out first."""
    solution = model.getBestSol()
    values = resolved(outputs, lambda leaf: leaf if isinstance(leaf, bool) else read(number_in(solution, leaf)))
    current = {variable.getIndex(): solution[variable] for variable in variables}
    best = solution[objective] if objective is not None else None
    return values, current, best


def forbid(model, variables, current, index):
    """Forbid the assignment of the variables the outputs are built from."""
    differs = []
    for position, variable in enumerate(variables):
        value = current[variable.getIndex()]
        low, high = variable.getLbGlobal(), variable.getUbGlobal()
        if low == high:
            continue
        if variable.vtype() == "BINARY":
            differs.append(variable if value < 0.5 else 1 - variable)
            continue
        whole = round(value)
        if whole > low:
            below = model.addVar(name=f"_below_{index}_{position}", vtype="B")
            model.addConsIndicator(variable <= whole - 1, binvar=below)
            differs.append(below)
        if whole < high:
            above = model.addVar(name=f"_above_{index}_{position}", vtype="B")
            model.addConsIndicator(variable >= whole + 1, binvar=above)
            differs.append(above)
    if not differs:
        # Every declared variable is fixed: there is no other assignment.
        return False
    from pyscipopt import quicksum
    model.addCons(quicksum(differs) >= 1)
    return True


def solve(request):
    deadline = time.monotonic() + request["execution_timeout"]
    model, outputs = load(request["instance"])
    configure(model)
    objective = objective_of(model)
    variables = variables_of(outputs)
    limit = request["solution_limit"]
    if limit > 1:
        continuous = [v.getName() for v in variables if v.vtype() == "CONTINUOUS"]
        if continuous:
            return finish("unsupported", "Enumeration needs integer declared outputs; "
                                         f"{continuous[0]} is continuous")

    verdict = attempt(model, deadline)
    if verdict == "infeasible":
        return finish("unsat")
    if verdict == "unbounded":
        return finish("error", "The objective is unbounded")
    if verdict == "timelimit":
        return finish("timeout", "Candidate optimum was not proven" if objective is not None else "")
    if verdict != "solved":
        return finish("error", f"SCIP stopped with status {verdict}")

    integral = objective is not None and integral_objective(objective)
    seen, count, index = set(), 0, 0
    while True:
        values, current, best = snapshot(model, outputs, variables, objective)
        key = json.dumps(values, sort_keys=True)
        if key not in seen:
            seen.add(key)
            emit({"type": "solution", "values": values})
            count += 1
            if count >= limit:
                return finish("limit")
        model.freeTransform()
        if objective is not None:
            # Only assignments that achieve the proven optimum may be enumerated.
            pin(model, objective, best, integral)
            objective = None
        if not forbid(model, variables, current, index):
            return finish("complete")
        index += 1
        verdict = attempt(model, deadline)
        if verdict == "infeasible":
            return finish("complete")
        if verdict == "timelimit":
            return finish("timeout")
        if verdict != "solved":
            return finish("error", f"SCIP stopped with status {verdict}")


def worker_main():
    protocol_stream()
    try:
        request = json.loads((INPUT / "request.json").read_text())
        solve(request)
    except NotImplementedError as error:
        finish("unsupported", str(error))
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
    sys.stdout.flush()
    sys.stderr.flush()
    # Skip interpreter teardown: SCIP's destructors are the last place a crash can happen.
    os._exit(0)


if __name__ == "__main__":
    if "--worker" in sys.argv:
        worker_main()
    else:
        supervise()
