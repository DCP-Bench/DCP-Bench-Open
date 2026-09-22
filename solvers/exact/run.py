"""Runner protocol for the exact integration. Runs inside the image only.

A submission defines `build(instance)` returning `(solver, outputs)` for a
satisfaction problem, or `(solver, outputs, (direction, terms))` where `solver`
is an `exact.Exact`, direction is "minimize" or "maximize", and `terms` is the
objective as a list of `(coefficient, variable_name)` pairs.

Exact identifies variables by name, so `outputs` maps each declared output name
to variable names, or nested lists of them. Values come back as integers; the
evaluator compares a 0/1 integer and a Boolean as equal, so a variable declared
over 0..1 satisfies a Boolean output without any special handling.

Three things about this solver decide how the runner is written:

* `toOptimum` answers **`"SAT"`** when it proved the optimum. There is no
  `"OPTIMAL"`. `"TIMEOUT"` means the search stopped short.
* `hasSolution()` stays true after `"TIMEOUT"` and after `"UNSAT"`, so it is
  never the test for whether there is an answer. The returned state is.
* Exact minimises internally, so a maximisation's optimum comes back negated.
"""
import contextlib
import importlib.util
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish, flatten, mapped  # noqa: E402

from exact import Exact  # noqa: E402

DIRECTIONS = ("minimize", "maximize")


def load(instance):
    """Import the submission and normalise what it returned."""
    spec = importlib.util.spec_from_file_location("candidate", "/input/model.py")
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        returned = module.build(instance)
    if not isinstance(returned, tuple) or len(returned) not in (2, 3):
        raise ValueError("build(instance) must return (solver, outputs) or "
                         "(solver, outputs, (direction, terms))")
    solver, outputs = returned[0], returned[1]
    objective = returned[2] if len(returned) == 3 else None
    if not isinstance(solver, Exact):
        raise ValueError("the first value must be an exact.Exact")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return a nonempty output dictionary")
    for leaf in flatten(outputs):
        if not isinstance(leaf, str):
            raise ValueError("an output leaf must be a variable name; got "
                             f"{type(leaf).__name__}")
    if objective is not None:
        if (not isinstance(objective, (tuple, list)) or len(objective) != 2
                or objective[0] not in DIRECTIONS):
            raise ValueError('the objective must be ("minimize", terms) or '
                             '("maximize", terms), with terms a list of '
                             "(coefficient, variable name) pairs")
    return solver, outputs, objective


def main():
    request = json.loads(Path("/input/request.json").read_text())
    if request.get("legacy"):
        return finish("unsupported", "This integration has no legacy submission format")

    started = time.monotonic()
    deadline = started + request["execution_timeout"]
    solver, outputs, objective = load(request["instance"])
    names = flatten(outputs)

    if objective is not None:
        direction, terms = objective
        minimise = direction == "minimize"
        solver.setObjective(list(terms), minimize=minimise)
        left = deadline - time.monotonic()
        if left <= 0:
            return finish("timeout", "the budget ran out before the search began",
                          solve_seconds=time.monotonic() - started)
        state, value = solver.toOptimum(left)
        spent = time.monotonic() - started
        if state == "UNSAT":
            return finish("unsat", solve_seconds=spent)
        if state != "SAT":
            # "TIMEOUT", and anything else, means the optimum was not proven.
            # Exact still holds a solution, which must not be reported as one.
            return finish("timeout", f"the optimum was not proven ({state})",
                          solve_seconds=spent)
        optimum = value if minimise else -value
        # Pin the objective so every further solution is an optimal one.
        solver.addConstraint(list(terms), True, optimum, True, optimum)

    limit = request["solution_limit"]
    emitted = 0
    while emitted < limit:
        left = deadline - time.monotonic()
        if left <= 0:
            return finish("timeout", "the budget ran out before the search finished",
                          solve_seconds=time.monotonic() - started)
        state = solver.runFull(False, left)
        spent = time.monotonic() - started
        if state == "UNSAT":
            return finish("complete" if emitted else "unsat", solve_seconds=spent)
        if state != "SAT":
            return finish("timeout", f"the search did not finish ({state})",
                          solve_seconds=spent)
        values = dict(zip(names, solver.getLastSolutionFor(names)))
        emit({"type": "solution", "values": mapped(outputs, values.__getitem__)})
        emitted += 1
        if emitted >= limit:
            break
        # Exact's own blocking, projected onto the declared outputs, so two
        # answers that differ only in auxiliary variables count as one.
        solver.invalidateLastSol(names)
    finish("limit", solve_seconds=time.monotonic() - started)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
