"""Runner protocol for the choco_python integration. Runs inside the image only.

A submission defines `build(instance)` returning `(model, outputs)`, or
`(model, outputs, (direction, objective))` for an optimization problem where
direction is "minimize" or "maximize" and objective is an IntVar of that model.

The runner owns solving. Two things about Choco shape how it does that.

Choco reports neither "search exhausted" nor "stopped at the limit" through
pychoco 0.2.1, so this runner times its own search: it sets Choco's limit to the
budget it has left and, when `solve()` returns false, calls it exhaustion only if
the search stopped comfortably before that limit. The margin is deliberately
generous, because reporting a timeout as exhaustion would turn a partial search
into a false "complete".

Choco enumerates distinct assignments of every variable, not of the declared
outputs, so two successive solutions can agree on everything the problem
declares. The runner therefore keeps a set of the declared-output tuples it has
already emitted and skips repeats rather than posting no-good constraints, which
pychoco cannot add once search has begun.
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

INPUT = Path("/input")
DIRECTIONS = ("minimize", "maximize")
# A search that stops with this much of its budget left really did run out of
# tree rather than out of time.
EXHAUSTION_MARGIN = 0.5


def load(instance):
    """Import the submission afresh and normalise what it returned.

    The model is rebuilt rather than reused between the optimization pass and
    the enumeration pass, because a Choco solver cannot be rewound once its
    search has started.
    """
    spec = importlib.util.spec_from_file_location("candidate", str(INPUT / "model.py"))
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        returned = module.build(instance)
    if not isinstance(returned, tuple) or len(returned) not in (2, 3):
        raise ValueError("build(instance) must return (model, outputs) or "
                         "(model, outputs, (direction, objective))")
    model, outputs = returned[0], returned[1]
    if not hasattr(model, "get_solver"):
        raise ValueError("build(instance) must return a pychoco Model as its first value")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return a nonempty output dictionary")
    objective = returned[2] if len(returned) == 3 else None
    if objective is not None:
        if (not isinstance(objective, (tuple, list)) or len(objective) != 2
                or objective[0] not in DIRECTIONS):
            raise ValueError('The objective must be ("minimize", variable) or '
                             '("maximize", variable)')
        if not hasattr(objective[1], "get_value"):
            raise ValueError("The objective must be a Choco variable, not an expression; "
                             "post an equality onto an IntVar and pass that")
    return model, outputs, objective


def read(expression):
    """One declared output value: an integer or a Boolean, never anything else."""
    if isinstance(expression, bool):
        return expression
    if isinstance(expression, int):
        return expression
    if not hasattr(expression, "get_value"):
        raise ValueError("Declared outputs must be Choco variables, integers or Booleans "
                         f"(got {expression!r})")
    value = expression.get_value()
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    raise ValueError("Declared outputs must be integer or Boolean values; no coercion "
                     f"from other types (got {value!r} for {expression!r})")


def remaining(deadline):
    return deadline - time.monotonic()


def limit(solver, seconds):
    """Give Choco the budget left, in whole milliseconds and never zero."""
    solver.limit_time(f"{max(1, int(seconds * 1000))}ms")


def best_objective(instance, direction, deadline):
    """Prove the optimal objective value, or say why it could not be proven.

    Choco's branch and bound only establishes optimality when its search runs to
    completion, so a run that used its whole budget is reported as a timeout even
    though it holds an incumbent.
    """
    left = remaining(deadline)
    if left <= 0:
        return None, ("timeout", "")
    model, _outputs, objective = load(instance)
    solver = model.get_solver()
    limit(solver, left)
    started = time.monotonic()
    solution = solver.find_optimal_solution(objective[1], maximize=direction == "maximize")
    spent = time.monotonic() - started
    if solution is None:
        # Either nothing satisfies the constraints, or the budget ran out before
        # anything was found; the elapsed time is what tells them apart.
        if spent < left - EXHAUSTION_MARGIN:
            return None, ("unsat", "")
        return None, ("timeout", "")
    if spent >= left - EXHAUSTION_MARGIN:
        return None, ("timeout", "Candidate optimum was not proven")
    return solution.get_int_val(objective[1]), None


def solve(request):
    deadline = time.monotonic() + request["execution_timeout"]
    instance = request["instance"]
    model, outputs, objective = load(instance)

    if objective is not None:
        best, failure = best_objective(instance, objective[0], deadline)
        if failure is not None:
            return finish(failure[0], failure[1])
        # Rebuild, then hold the objective at the proven optimum so that only
        # optimal assignments are enumerated.
        model, outputs, objective = load(instance)
        model.arithm(objective[1], "=", best).post()

    flat = flatten(outputs)
    solver = model.get_solver()
    left = remaining(deadline)
    if left <= 0:
        return finish("timeout")
    limit(solver, left)

    seen = set()
    started = time.monotonic()
    while len(seen) < request["solution_limit"]:
        if not solver.solve():
            spent = time.monotonic() - started
            if spent >= left - EXHAUSTION_MARGIN:
                return finish("timeout")
            # The search really is exhausted: everything there was has been seen.
            return finish("complete" if seen else "unsat")
        fingerprint = tuple(read(expression) for expression in flat)
        if fingerprint in seen:
            # Choco varied something the problem does not declare; keep looking.
            continue
        seen.add(fingerprint)
        emit({"type": "solution", "values": mapped(outputs, read)})
    finish("limit")


def main():
    try:
        request = json.loads((INPUT / "request.json").read_text())
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by choco_python")

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
