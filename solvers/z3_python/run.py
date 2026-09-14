"""Runner protocol for the z3_python integration. Runs inside the image only.

A submission defines `build(instance)` returning `(constraints, outputs)`, or
`(constraints, outputs, (direction, objective))` for an optimization problem
where direction is "minimize" or "maximize". The runner owns solving: it proves
the optimum itself rather than trusting a single `check()`, enumerates distinct
declared outputs by blocking, and never reports success on an unproven optimum.
"""
import contextlib
import importlib.util
import json
from pathlib import Path
import signal
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish, flatten, mapped  # noqa: E402

import z3  # noqa: E402

INPUT = Path("/input")
DIRECTIONS = ("minimize", "maximize")


def load(instance):
    """Import the submission and normalise what it returned."""
    spec = importlib.util.spec_from_file_location("candidate", str(INPUT / "model.py"))
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        returned = module.build(instance)
    if not isinstance(returned, tuple) or len(returned) not in (2, 3):
        raise ValueError("build(instance) must return (constraints, outputs) or "
                         "(constraints, outputs, (direction, objective))")
    constraints, outputs = returned[0], returned[1]
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return a nonempty output dictionary")
    objective = returned[2] if len(returned) == 3 else None
    if objective is not None:
        if (not isinstance(objective, (tuple, list)) or len(objective) != 2
                or objective[0] not in DIRECTIONS):
            raise ValueError('The objective must be ("minimize", expression) or '
                             '("maximize", expression)')
    return assertions(constraints), outputs, objective


def assertions(constraints):
    """Accept a Solver, an Optimize, a sequence of constraints, or one constraint."""
    if hasattr(constraints, "assertions"):
        return list(constraints.assertions())
    if isinstance(constraints, (list, tuple)):
        return list(constraints)
    return [constraints]


def read(expression, model):
    """One declared output value: an integer or a Boolean, never a real."""
    if isinstance(expression, bool):
        return expression
    if isinstance(expression, int):
        return expression
    value = model.eval(expression, model_completion=True)
    if z3.is_true(value):
        return True
    if z3.is_false(value):
        return False
    if isinstance(value, z3.IntNumRef):
        return value.as_long()
    raise ValueError("Declared outputs must be integer or Boolean values; no coercion "
                     f"from reals or other sorts (got {value} for {expression})")


def blocking(expressions, model):
    """Forbid this exact assignment of the declared outputs."""
    clause = [expression != model.eval(expression, model_completion=True)
              for expression in expressions if not isinstance(expression, (bool, int))]
    # With only constant outputs there is a single possible assignment, so
    # nothing further exists to find.
    return z3.Or(*clause) if clause else z3.BoolVal(False)


def remaining(deadline):
    left = deadline - time.monotonic()
    return None if left <= 0 else max(1, int(left * 1000))


def optimum(constraints, direction, objective, deadline):
    """Prove the optimal objective value, or say why it could not be proven."""
    optimizer = z3.Optimize()
    optimizer.add(constraints)
    handle = (optimizer.minimize if direction == "minimize" else optimizer.maximize)(objective)
    budget = remaining(deadline)
    if budget is None:
        return None, ("timeout", "")
    optimizer.set("timeout", budget)
    status = optimizer.check()
    if status == z3.unsat:
        return None, ("unsat", "")
    if status != z3.sat:
        return None, ("timeout", "")
    low, high = optimizer.lower(handle), optimizer.upper(handle)
    if not (isinstance(low, z3.IntNumRef) and isinstance(high, z3.IntNumRef)):
        return None, ("error", f"Objective is not a finite integer between {low} and {high}")
    if low.as_long() != high.as_long():
        return None, ("timeout", "Candidate optimum was not proven")
    return low.as_long(), None


def solve(request):
    deadline = time.monotonic() + request["execution_timeout"]
    constraints, outputs, objective = load(request["instance"])
    flat = flatten(outputs)

    if objective is not None:
        best, failure = optimum(constraints, objective[0], objective[1], deadline)
        if failure is not None:
            return finish(failure[0], failure[1])
        # Enumerate only assignments achieving the proven optimum.
        constraints = constraints + [objective[1] == best]

    solver = z3.Solver()
    solver.add(constraints)
    count = 0
    while count < request["solution_limit"]:
        budget = remaining(deadline)
        if budget is None:
            return finish("timeout")
        solver.set("timeout", budget)
        status = solver.check()
        if status == z3.unsat:
            return finish("complete" if count else "unsat")
        if status != z3.sat:
            return finish("timeout")
        model = solver.model()
        emit({"type": "solution", "values": mapped(outputs, lambda e: read(e, model))})
        count += 1
        if count == request["solution_limit"]:
            break
        solver.add(blocking(flat, model))
    finish("limit")


def main():
    try:
        request = json.loads((INPUT / "request.json").read_text())
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by z3_python")

        def expired(signum, frame):
            raise TimeoutError("Runner execution budget exceeded")

        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, request["execution_timeout"] + 5)
        solve(request)
    except TimeoutError:
        finish("timeout")
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))


if __name__ == "__main__":
    main()
