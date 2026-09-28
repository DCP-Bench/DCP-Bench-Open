"""Runner protocol for the docplex_cplex integration. Runs inside the image only.

A submission defines `build(instance)` returning `(model, outputs)`, where
`model` is a `docplex.mp.model.Model`. Its own objective says whether this is
an optimization: `has_objective()` is false until `minimize` or `maximize` is
given a non-constant expression, so the submission needs no extra convention.

Four things about CPLEX shape this runner.

CPLEX stops once the incumbent is within `mip.tolerances.mipgap` of the bound,
1e-4 relative by default, and calls that "integer optimal, tolerance". On a
40-item knapsack that status came back 393 short of the optimum. The runner
sets the relative gap to 0, so an optimal status means proven, whatever the
submission set.

Integer variables come back within `mip.tolerances.integrality` (1e-5) of an
integer rather than on it. The runner rounds every integer variable and
evaluates declared linear expressions over the rounded values; any other
declared value must itself be within 1e-6 of an integer.

The Community Edition in the cplex wheel refuses a model above 1000 variables
or 1000 constraints (indicator constraints included). That is reported as
`unsupported` with CPLEX's own message, never as a timeout or a fault in the
model.

CPLEX returns one solution rather than a stream, so enumeration pins the
objective to the proven optimum and adds a no-good over the integer variables
the declared outputs are built from: a linear one for binaries, and indicator
constraints for general integers, which need no bound.

CPLEX prints some errors from C, below Python's `sys.stdout`, so the protocol
stream keeps file descriptor 1 to itself and everything else written to stdout
goes to stderr.
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

from docplex.mp.model import Model  # noqa: E402
from docplex.mp.utils import DOcplexLimitsExceeded  # noqa: E402

INPUT = Path("/input")
# A declared output has to be an integer; a value further from one than this is
# a modelling error rather than solver noise.
TOLERANCE = 1e-6
# CPLEX solution status codes, as docplex reports them in solve_details.
PROVEN = {1, 101, 102}      # optimal (LP), integer optimal, integer optimal within tolerance
INFEASIBLE = {3, 103}
AMBIGUOUS = {4, 119}        # infeasible or unbounded
UNBOUNDED = {2, 118}
TIMED_OUT = {11, 107, 108}  # time limit, with or without a solution


def protocol_stream():
    """Give the JSONL protocol its own copy of fd 1 and send fd 1 to stderr."""
    protocol = os.dup(1)
    os.dup2(2, 1)
    sys.stdout = os.fdopen(protocol, "w", buffering=1)


def is_expression(value):
    """A docplex variable or expression, as opposed to a container or a number."""
    return hasattr(value, "solution_value") or hasattr(value, "iter_terms")


def leaves(value):
    """Every declared output value, with docplex expressions left whole."""
    if isinstance(value, dict):
        return [x for v in value.values() for x in leaves(v)]
    if isinstance(value, (list, tuple)):
        return [x for v in value for x in leaves(v)]
    if hasattr(value, "tolist") and not is_expression(value):
        return leaves(value.tolist())
    return [value]


def resolved(value, read_one):
    """The declared outputs with every leaf replaced by its integer value."""
    if isinstance(value, dict):
        return {k: resolved(v, read_one) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [resolved(v, read_one) for v in value]
    if hasattr(value, "tolist") and not is_expression(value):
        return resolved(value.tolist(), read_one)
    return read_one(value)


def integer(variable):
    return variable.vartype.short_name in ("binary", "integer")


def is_variable(value):
    return hasattr(value, "vartype")


def variable_value(variable):
    """An integer variable rounded to the integer its tolerance allows."""
    value = variable.solution_value
    return round(value) if integer(variable) else value


def terms(value):
    """The variables a declared value is built from."""
    if is_variable(value):
        return [value]
    if hasattr(value, "iter_terms"):
        return [variable for variable, _ in value.iter_terms()]
    if hasattr(value, "as_var"):
        return [value.as_var]
    return []


def value_of(value):
    """The value of a variable or linear expression over rounded integer variables."""
    if is_variable(value):
        return variable_value(value)
    if hasattr(value, "iter_terms") and hasattr(value, "constant"):
        return value.constant + sum(coefficient * variable_value(variable)
                                    for variable, coefficient in value.iter_terms())
    return value.solution_value


def integral(expression):
    """Whether the expression can only take integer values."""
    if is_variable(expression):
        return integer(expression)
    if not (hasattr(expression, "iter_terms") and hasattr(expression, "constant")):
        return False
    pairs = list(expression.iter_terms())
    return (float(expression.constant).is_integer()
            and all(float(c).is_integer() and integer(v) for v, c in pairs))


def read(value):
    """One declared output value: an integer, never a float from the solver."""
    if isinstance(value, bool):
        return value
    if isinstance(value, numbers.Integral):
        return int(value)
    number = value if isinstance(value, numbers.Real) else value_of(value)
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
    if not isinstance(model, Model):
        raise ValueError("build(instance) must return a docplex.mp.model.Model")
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
        low, high = variable.lb, variable.ub
        if low == high:
            continue
        if low >= 0 and high <= 1:
            # A binary differs from its value through a linear term alone.
            differs.append(variable if value == 0 else 1 - variable)
            continue
        if value > low:
            below = model.binary_var(name=f"_below_{index}_{position}")
            model.add_indicator(below, variable <= value - 1, active_value=1)
            differs.append(below)
        if value < high:
            above = model.binary_var(name=f"_above_{index}_{position}")
            model.add_indicator(above, variable >= value + 1, active_value=1)
            differs.append(above)
    if not differs:
        # Every declared variable is pinned to its only value: nothing else exists.
        return False
    model.add_constraint(model.sum(differs) >= 1, ctname=f"_nogood_{index}")
    return True


def pin(model, objective):
    """Keep only assignments at the proven optimum, then search for any of them."""
    best = value_of(objective)
    if integral(objective):
        best = round(best)
        low, high = best - 0.5, best + 0.5
    else:
        slack = TOLERANCE * max(1.0, abs(best))
        low, high = best - slack, best + slack
    model.add_range(low, objective, high, rng_name="_optimum")
    model.remove_objective()


def attempt(model, deadline):
    """Solve once inside the remaining budget; say what CPLEX actually concluded."""
    left = deadline - time.monotonic()
    if left <= 0:
        return "timeout"
    model.parameters.timelimit = left
    with contextlib.redirect_stdout(sys.stderr):
        solution = model.solve(log_output=False)
    code = model.solve_details.status_code
    if code in AMBIGUOUS:
        # Presolve stopped before telling the two apart; without its dual
        # reductions it has to.
        left = deadline - time.monotonic()
        if left <= 0:
            return "timeout"
        model.parameters.preprocessing.reduce = 1  # primal reductions only
        model.parameters.timelimit = left
        with contextlib.redirect_stdout(sys.stderr):
            solution = model.solve(log_output=False)
        code = model.solve_details.status_code
    if code in PROVEN and solution is not None:
        return "solved"
    if code in INFEASIBLE:
        return "infeasible"
    if code in UNBOUNDED:
        return "unbounded"
    if code in TIMED_OUT:
        return "timeout"
    return f"{code} ({model.solve_details.status})"


def configure(model):
    """The settings that decide what a verdict means; they override the submission's."""
    model.parameters.threads = 1
    model.parameters.mip.tolerances.mipgap = 0


def solve(request):
    deadline = time.monotonic() + request["execution_timeout"]
    model, outputs = load(request["instance"])
    configure(model)
    objective = model.objective_expr if model.has_objective() else None
    variables = cut_variables(outputs)

    verdict = attempt(model, deadline)
    if verdict == "infeasible":
        return finish("unsat")
    if verdict == "unbounded":
        return finish("error", "The objective is unbounded")
    if verdict == "timeout":
        return finish("timeout", "Candidate optimum was not proven" if objective is not None else "")
    if verdict != "solved":
        return finish("error", f"CPLEX stopped with status {verdict}")

    limit = request["solution_limit"]
    if limit > 1:
        continuous = [v.name for v in variables if not integer(v)]
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
            return finish("error", f"CPLEX stopped with status {verdict}")


def main():
    protocol_stream()
    try:
        request = json.loads((INPUT / "request.json").read_text())
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by docplex_cplex")

        def expired(signum, frame):
            raise TimeoutError("Runner execution budget exceeded")

        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, request["execution_timeout"] + 5)
        solve(request)
    except TimeoutError:
        finish("timeout")
    except DOcplexLimitsExceeded as error:
        finish("unsupported", "The model is larger than the CPLEX Community Edition in the cplex "
                              f"wheel allows (1000 variables, 1000 constraints): {error}")
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))


if __name__ == "__main__":
    main()
