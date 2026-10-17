"""Runner protocol for the mip_cbc integration. Runs inside the image only.

A submission defines `build(instance)` returning `(model, outputs)`, where `model` is a
`mip.Model` (Python-MIP, default solver CBC) and `outputs` maps each declared output to a
variable, a linear expression, an integer or Boolean, or a nested list/tuple/dict of these.
Whether the model optimises is read from its objective: a model with no objective terms
and a zero constant is a satisfaction problem, whatever its `sense`.

Three things about Python-MIP and CBC shape this runner.

CBC reports OPTIMAL when its gap is within `max_mip_gap` (default 1e-4) and
`max_mip_gap_abs`, so every solve here runs with both set to zero. Then OPTIMAL means
proven, and FEASIBLE or NO_SOLUTION_FOUND after the time limit is `timeout`.

CBC writes its log to the C-level stdout (file descriptor 1), which Python cannot
redirect. Descriptor 1 is pointed at stderr for the whole run, and protocol records go to a
saved copy of it.

A MIP solver returns one solution rather than a stream, so enumeration is done by excluding
what was already found: the objective is pinned to the proven optimum, and each further
solve adds a no-good over the integer variables the declared outputs are built from. That
needs those variables to be integral and bounded, and says so when they are not.
"""
import contextlib
import importlib.util
import json
import math
import numbers
import os
from pathlib import Path
import signal
import sys
import time
import traceback

PROTOCOL = os.fdopen(os.dup(1), "w", buffering=1)
os.dup2(2, 1)
sys.stdout = sys.stderr
sys.path.insert(0, "/opt/runner")

import runtime  # noqa: E402

import mip  # noqa: E402
from mip import OptimizationStatus, xsum  # noqa: E402

INPUT = Path("/input")
# CBC returns floats. A declared output is an integer, and a value further from one than
# this is a modelling error rather than solver noise.
TOLERANCE = 1e-6


class Expired(Exception):
    """The execution budget ran out (raised by SIGALRM)."""


@contextlib.contextmanager
def protocol_stdout():
    saved = sys.stdout
    sys.stdout = PROTOCOL
    try:
        yield
    finally:
        sys.stdout = saved


def emit(record):
    with protocol_stdout():
        runtime.emit(record)


def finish(status, detail="", **metadata):
    with protocol_stdout():
        runtime.finish(status, detail, **metadata)


def leaves(value):
    """Every declared output leaf. Variables and expressions are leaves, not containers."""
    if isinstance(value, (mip.Var, mip.LinExpr)):
        return [value]
    if isinstance(value, dict):
        return [x for v in value.values() for x in leaves(v)]
    if isinstance(value, (list, tuple)):
        return [x for v in value for x in leaves(v)]
    return [value]


def resolved(value):
    """The declared outputs with every leaf replaced by its integer value."""
    if isinstance(value, dict):
        return {k: resolved(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [resolved(v) for v in value]
    return read(value)


def read(value):
    """One declared output value: an integer or a Boolean, never a float from the solver."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (mip.Var, mip.LinExpr)):
        number = value.x
        if number is None:
            raise ValueError("A declared output has no value; every output must be a "
                             "variable or expression the model constrains")
    elif isinstance(value, numbers.Real):
        number = value
    else:
        raise ValueError("Declared outputs must be integer or Boolean values, got "
                         f"{type(value).__name__}")
    rounded = round(number)
    if abs(number - rounded) > TOLERANCE:
        raise ValueError("Declared outputs must be integer valued; no coercion from "
                         f"fractional values (got {number})")
    return int(rounded)


def load(instance):
    spec = importlib.util.spec_from_file_location("candidate", str(INPUT / "model.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    returned = module.build(instance)
    if not isinstance(returned, tuple) or len(returned) != 2:
        raise ValueError("build(instance) must return (model, outputs)")
    model, outputs = returned
    if not isinstance(model, mip.Model):
        raise ValueError("build(instance) must return a mip.Model")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return a nonempty output dictionary")
    return model, outputs


def force_settings(model):
    model.verbose = 0
    model.threads = 1
    model.max_mip_gap = 0.0
    model.max_mip_gap_abs = 0.0


def cut_variables(outputs):
    """The variables a no-good cut has to move, one per index."""
    collected = {}
    for leaf in leaves(outputs):
        if isinstance(leaf, mip.Var):
            found = [leaf]
        elif isinstance(leaf, mip.LinExpr):
            found = list(leaf.expr.keys())
        else:
            found = []
        for variable in found:
            collected[variable.idx] = variable
    return list(collected.values())


def enumerable(variables):
    """Why these variables cannot carry a no-good cut, or None if they can."""
    for variable in variables:
        if variable.var_type == mip.CONTINUOUS:
            return f"Enumeration needs integer declared outputs; {variable.name} is continuous"
        if not (math.isfinite(variable.lb) and math.isfinite(variable.ub)):
            return (f"Enumeration needs bounded declared outputs; {variable.name} has no "
                    "finite lower and upper bound")
    return None


def forbid(model, variables, index):
    """Forbid the assignment the variables currently hold. False if none can differ."""
    indicators = []
    for position, variable in enumerate(variables):
        value = round(variable.x)
        low, high = math.ceil(variable.lb), math.floor(variable.ub)
        if value > low:
            below = model.add_var(name=f"_below_{index}_{position}", var_type=mip.BINARY)
            model += variable <= value - 1 + (high - value + 1) * (1 - below)
            indicators.append(below)
        if value < high:
            above = model.add_var(name=f"_above_{index}_{position}", var_type=mip.BINARY)
            model += variable >= value + 1 - (value + 1 - low) * (1 - above)
            indicators.append(above)
    if not indicators:
        return False
    model += xsum(indicators) >= 1
    return True


def attempt(model, deadline, optimizing):
    """Solve once inside the remaining budget; say what CBC actually concluded."""
    left = deadline - time.monotonic()
    if left <= 0:
        return "timeout"
    status = model.optimize(max_seconds=left)
    if status == OptimizationStatus.OPTIMAL:
        return "solved"
    if status in (OptimizationStatus.INFEASIBLE, OptimizationStatus.INT_INFEASIBLE):
        return "infeasible"
    if status == OptimizationStatus.UNBOUNDED:
        return "unbounded"
    if status == OptimizationStatus.FEASIBLE and not optimizing:
        # A satisfaction problem: any feasible point is an answer, no proof is needed.
        return "solved"
    if status in (OptimizationStatus.FEASIBLE, OptimizationStatus.NO_SOLUTION_FOUND):
        return "timeout"
    raise RuntimeError(f"Python-MIP returned status {status.name}")


def solve(request):
    deadline = time.monotonic() + request["execution_timeout"]
    model, outputs = load(request["instance"])
    force_settings(model)
    optimizing = bool(model.objective.expr) or model.objective.const != 0
    limit = request["solution_limit"]
    variables = cut_variables(outputs)

    verdict = attempt(model, deadline, optimizing)
    if verdict == "infeasible":
        return finish("unsat")
    if verdict == "unbounded":
        return finish("error", "The objective is unbounded")
    if verdict != "solved":
        return finish("timeout", "Optimum not proven within the time limit" if optimizing
                      else "No solution found within the time limit")

    if limit > 1:
        obstacle = enumerable(variables)
        if obstacle is not None:
            return finish("unsupported", obstacle)
        if optimizing:
            # Only assignments that achieve the proven optimum may be enumerated.
            best = model.objective_value
            model += model.objective <= best + TOLERANCE
            model += model.objective >= best - TOLERANCE

    seen, count, index = set(), 0, 0
    while True:
        values = resolved(outputs)
        key = json.dumps(values, sort_keys=True)
        if key not in seen:
            seen.add(key)
            emit({"type": "solution", "values": values})
            count += 1
            if count >= limit:
                return finish("limit")
        if not forbid(model, variables, index):
            return finish("complete")
        index += 1
        verdict = attempt(model, deadline, optimizing)
        if verdict == "infeasible":
            return finish("complete")
        if verdict == "unbounded":
            return finish("error", "The objective is unbounded")
        if verdict != "solved":
            return finish("timeout")


def expired(signum, frame):
    raise Expired("Runner execution budget exceeded")


def main():
    try:
        request = json.loads((INPUT / "request.json").read_text())
        if request.get("legacy"):
            return finish("unsupported", "Legacy submissions are not supported by mip_cbc")
        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(signal.ITIMER_REAL, request["execution_timeout"] + 5)
        solve(request)
    except Expired:
        finish("timeout")
    except Exception as error:
        traceback.print_exc(file=sys.stderr)
        finish("error", f"{type(error).__name__}: {error}")


if __name__ == "__main__":
    main()
