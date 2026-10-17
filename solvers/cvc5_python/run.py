"""Runner protocol for the cvc5_python integration. Runs inside the image only.

A submission defines `build(instance)` returning `(constraints, outputs)`, or
`(constraints, outputs, (direction, objective))` for an optimization problem
where direction is "minimize" or "maximize". The submission uses cvc5's
pythonic API (`cvc5.pythonic`). cvc5 has no optimiser, so the runner proves the
optimum itself: it tightens the objective until unsat, enumerates distinct
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

import cvc5.pythonic as cz  # noqa: E402

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
        if isinstance(objective[1], int) and not isinstance(objective[1], bool):
            objective = (objective[0], cz.IntVal(objective[1]))
    return assertions(constraints), configuration(constraints), outputs, objective


# Options the runner sets itself: a returned Solver's values for these are not copied.
OWNED = ("incremental", "produce-models", "tlimit", "tlimit-per")


def configuration(constraints):
    """The logic and the user-set options of a returned Solver, as (logic, options).

    The runner solves on fresh solvers, so it reproduces these on each of them.
    A list of constraints, or a Solver that sets nothing, gives (None, {}).
    """
    if not isinstance(constraints, cz.Solver):
        return None, {}
    native = constraints.solver
    logic = native.getLogic() if native.isLogicSet() else None
    options = {name: native.getOption(name) for name in native.getOptionNames()
               if name not in OWNED and native.getOptionInfo(name)["setByUser"]}
    return logic, options


def fresh(configuration):
    """A new pythonic Solver with the returned Solver's logic and options."""
    logic, options = configuration
    solver = cz.Solver() if logic is None else cz.SolverFor(logic)
    for name, value in options.items():
        solver.set(name, value)
    return solver


def assertions(constraints):
    """Accept a cvc5 pythonic Solver, a sequence of constraints, or one constraint."""
    if isinstance(constraints, cz.Solver):
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
    if cz.is_true(value):
        return True
    if cz.is_false(value):
        return False
    if isinstance(value, cz.IntNumRef):
        return value.as_long()
    raise ValueError("Declared outputs must be integer or Boolean values; no coercion "
                     f"from reals or other sorts (got {value} for {expression})")


def blocking(expressions, model):
    """Forbid this exact assignment of the declared outputs."""
    clause = [expression != model.eval(expression, model_completion=True)
              for expression in expressions if not isinstance(expression, (bool, int))]
    # With only constant outputs there is a single possible assignment, so
    # nothing further exists to find.
    return cz.Or(*clause) if clause else cz.BoolVal(False)


def remaining(deadline):
    left = deadline - time.monotonic()
    return None if left <= 0 else max(1, int(left * 1000))


def check(solver, deadline):
    """One check under the time left: (result, None), or (None, (status, detail)) when out of budget."""
    budget = remaining(deadline)
    if budget is None:
        return None, ("timeout", "")
    # tlimit-per is the limit of one check() call; 0 would mean no limit.
    solver.set("tlimit-per", budget)
    result = solver.check()
    if result == cz.unknown:
        reason = str(solver.reason_unknown())
        if reason.endswith("TIMEOUT"):
            return None, ("timeout", "")
        return None, ("error", f"cvc5 returned unknown: {reason}")
    return result, None


def optimum(constraints, setup, direction, objective, deadline):
    """Prove the optimal objective value, or say why it could not be proven.

    Each step asserts a strictly better objective on one incremental solver. The
    last model found is the optimum once the next step is unsat; unknown or
    running out of time before that is `timeout`.
    """
    solver = fresh(setup)
    solver.add(constraints)
    best = None
    while True:
        result, failure = check(solver, deadline)
        if failure is not None:
            return None, failure
        if result == cz.unsat:
            if best is None:
                return None, ("unsat", "")
            return best, None
        model = solver.model()
        value = model.eval(objective, model_completion=True)
        if not isinstance(value, cz.IntNumRef):
            return None, ("error", "Objective is not an integer expression")
        best = value.as_long()
        if direction == "minimize":
            solver.add(objective < best)
        else:
            solver.add(objective > best)


def solve(request):
    deadline = time.monotonic() + request["execution_timeout"]
    constraints, setup, outputs, objective = load(request["instance"])
    flat = flatten(outputs)

    if objective is not None:
        best, failure = optimum(constraints, setup, objective[0], objective[1], deadline)
        if failure is not None:
            return finish(failure[0], failure[1])
        # Enumerate only assignments achieving the proven optimum.
        constraints = constraints + [objective[1] == best]

    solver = fresh(setup)
    solver.add(constraints)
    count = 0
    while count < request["solution_limit"]:
        result, failure = check(solver, deadline)
        if failure is not None:
            return finish(failure[0], failure[1])
        if result == cz.unsat:
            return finish("complete" if count else "unsat")
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
            return finish("unsupported", "Legacy submissions are not supported by cvc5_python")

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
