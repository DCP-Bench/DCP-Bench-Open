"""Runner protocol for the pulp_cbc integration. Runs inside the image only.

A submission defines `build(instance)` returning `(problem, outputs)`, where
`problem` is a `pulp.LpProblem`. Its own `objective` says whether this is an
optimization: PuLP leaves it `None` until something is added to it, and its
`sense` says which direction, so the submission needs no extra convention.

Two things about CBC shape this runner.

CBC reports `status == LpStatusOptimal` even when it stopped on the time limit;
only `sol_status` separates a proven optimum (`LpSolutionOptimal`) from a
feasible point it never proved (`LpSolutionIntegerFeasible`). Reporting the
second as success would let an unproven optimum pass, so every solve here is
judged on `sol_status`.

A MIP solver also returns one solution rather than a stream, so enumeration is
done by excluding what was already found: the objective is pinned to the proven
optimum and each further solve adds a no-good cut over the integer variables the
declared outputs are built from. That needs those variables to be integral and
bounded, and says so explicitly when they are not.
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

import pulp  # noqa: E402

INPUT = Path("/input")
# CBC returns floats; a declared output has to be an integer, and anything
# further from one than this is a modelling error rather than solver noise.
TOLERANCE = 1e-6


def load(instance):
    spec = importlib.util.spec_from_file_location("candidate", str(INPUT / "model.py"))
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        returned = module.build(instance)
    if not isinstance(returned, tuple) or len(returned) != 2:
        raise ValueError("build(instance) must return (problem, outputs)")
    problem, outputs = returned
    if not isinstance(problem, pulp.LpProblem):
        raise ValueError("build(instance) must return a pulp.LpProblem")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return a nonempty output dictionary")
    return problem, outputs


def read(expression):
    """One declared output value: an integer, never a float from the solver."""
    if isinstance(expression, bool):
        return expression
    value = expression if isinstance(expression, int) else pulp.value(expression)
    if value is None:
        raise ValueError("A declared output has no value; every output must be "
                         "a variable or expression the model constrains")
    rounded = round(value)
    if abs(value - rounded) > TOLERANCE:
        raise ValueError("Declared outputs must be integer valued; no coercion from "
                         f"fractional values (got {value})")
    return int(rounded)


def cut_variables(outputs):
    """The variables a no-good cut has to move, with their bounds."""
    collected = {}
    for leaf in flatten(outputs):
        if isinstance(leaf, pulp.LpVariable):
            found = [leaf]
        elif isinstance(leaf, pulp.LpAffineExpression):
            found = list(leaf.keys())
        else:
            found = []
        for variable in found:
            collected[variable.name] = variable
    return list(collected.values())


def enumerable(variables):
    """Why these variables cannot carry a no-good cut, or None if they can."""
    for variable in variables:
        if variable.cat == pulp.LpContinuous:
            return (f"Enumeration needs integer declared outputs; {variable.name} is continuous")
        if variable.lowBound is None or variable.upBound is None:
            return (f"Enumeration needs bounded declared outputs; {variable.name} has no "
                    "finite lower and upper bound")
    return None


def forbid(problem, variables, index):
    """Forbid the assignment the variables currently hold."""
    indicators = []
    for position, variable in enumerate(variables):
        value = round(pulp.value(variable))
        low, high = int(variable.lowBound), int(variable.upBound)
        if value > low:
            below = pulp.LpVariable(f"_below_{index}_{position}", cat=pulp.LpBinary)
            problem += variable <= value - 1 + (high - value + 1) * (1 - below)
            indicators.append(below)
        if value < high:
            above = pulp.LpVariable(f"_above_{index}_{position}", cat=pulp.LpBinary)
            problem += variable >= value + 1 - (value + 1 - low) * (1 - above)
            indicators.append(above)
    if not indicators:
        # Every declared variable is pinned to its only value: nothing else exists.
        return False
    problem += pulp.lpSum(indicators) >= 1
    return True


def attempt(problem, deadline):
    """Solve once inside the remaining budget; say what CBC actually concluded."""
    left = deadline - time.monotonic()
    if left <= 0:
        return "timeout"
    solver = pulp.PULP_CBC_CMD(msg=0, threads=1, timeLimit=max(1, int(left)))
    with contextlib.redirect_stdout(sys.stderr):
        problem.solve(solver)
    if problem.status == pulp.LpStatusInfeasible:
        return "infeasible"
    if problem.status == pulp.LpStatusUnbounded:
        return "unbounded"
    # CBC says Optimal when it stopped on time, so sol_status is the one to read.
    if problem.sol_status != pulp.LpSolutionOptimal:
        return "timeout"
    return "solved"


def solve(request):
    deadline = time.monotonic() + request["execution_timeout"]
    problem, outputs = load(request["instance"])
    optimizing = problem.objective is not None

    verdict = attempt(problem, deadline)
    if verdict == "infeasible":
        return finish("unsat")
    if verdict == "unbounded":
        return finish("error", "The objective is unbounded")
    if verdict != "solved":
        return finish("timeout", "Candidate optimum was not proven" if optimizing else "")

    limit = request["solution_limit"]
    variables = cut_variables(outputs)
    if limit > 1:
        obstacle = enumerable(variables)
        if obstacle is not None:
            return finish("unsupported", obstacle)
        if optimizing:
            # Only assignments that achieve the proven optimum may be enumerated.
            best = pulp.value(problem.objective)
            problem += problem.objective <= best + TOLERANCE
            problem += problem.objective >= best - TOLERANCE

    seen, count, index = set(), 0, 0
    while True:
        values = mapped(outputs, read)
        key = json.dumps(values, sort_keys=True)
        if key not in seen:
            seen.add(key)
            emit({"type": "solution", "values": values})
            count += 1
            if count >= limit:
                return finish("limit")
        if not forbid(problem, variables, index):
            return finish("complete")
        index += 1
        verdict = attempt(problem, deadline)
        if verdict == "infeasible":
            return finish("complete")
        if verdict != "solved":
            return finish("timeout")


def main():
    try:
        request = json.loads((INPUT / "request.json").read_text())
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by pulp_cbc")

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
