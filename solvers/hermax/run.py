"""Runner protocol for the hermax integration. Runs inside the image only.

A submission defines `build(instance)` returning `(sat, outputs)` for a
satisfaction problem, or `(sat, outputs, (direction, objective))` where
direction is "minimize" or "maximize" and objective is an `IntVar` of the same
builder.

A MaxSAT solver has no objective expression: it minimises the total weight of
the soft clauses it breaks. So the runner turns the objective variable's one-hot
literals into soft units, one per value. Minimising `x` makes "x is not v" worth
`v - min`, so the cost the solver reports is the objective value shifted down by
its minimum; maximising makes it worth `max - v` instead. Either way the cost
moves with the objective, so comparing costs compares objective values.

**The search runs in a child process.** No hermax backend accepts
`solve(time_limit=...)` or implements `set_terminate` -- both raise
NotImplementedError -- so there is no way to bound the search from inside the
process running it. The parent therefore supervises a child, which streams its
solution records to the shared stdout, and kills it when the budget runs out.
The parent emits a status only when the child failed to, which is exactly the
case where it was killed.

Optimality is reported only on `SolveStatus.OPTIMUM`. `INTERRUPTED_SAT` means a
solution was found without proving it best, which is a timeout here rather than
an answer, because the evaluator would otherwise compare it against the
reference optimum as if it were one.
"""
import contextlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish  # noqa: E402

from dcp_maxsat import IntVar, MaxSat  # noqa: E402

DIRECTIONS = ("minimize", "maximize")


def load(instance):
    spec = importlib.util.spec_from_file_location("candidate", "/input/model.py")
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        result = module.build(instance)
    if not isinstance(result, tuple) or len(result) not in (2, 3):
        raise ValueError("build(instance) must return (sat, outputs) or (sat, outputs, objective)")
    sat, outputs = result[0], result[1]
    objective = result[2] if len(result) == 3 else None
    if not isinstance(sat, MaxSat):
        raise ValueError("the first value must be the MaxSat builder from dcp_maxsat")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return a nonempty output dictionary")
    if objective is not None:
        if not isinstance(objective, tuple) or len(objective) != 2:
            raise ValueError("the objective must be (direction, IntVar)")
        direction, variable = objective
        if direction not in DIRECTIONS:
            raise ValueError(f"objective direction must be one of {DIRECTIONS}")
        if not isinstance(variable, IntVar):
            raise ValueError("the objective must be an IntVar, not an expression")
    return sat, outputs, objective


def leaves(node, found):
    if isinstance(node, dict):
        for value in node.values():
            leaves(value, found)
    elif isinstance(node, (list, tuple)):
        for value in node:
            leaves(value, found)
    else:
        found.append(node)
    return found


def render(node, truth):
    if isinstance(node, dict):
        return {name: render(value, truth) for name, value in node.items()}
    if isinstance(node, (list, tuple)):
        return [render(value, truth) for value in node]
    if isinstance(node, IntVar):
        return node.read(truth)
    if isinstance(node, bool):
        return node
    if isinstance(node, int):
        return node in truth
    raise ValueError(f"an output leaf must be an IntVar, a literal, an int or a bool; got {type(node).__name__}")


def blocking_clause(outputs, truth):
    """Rule out exactly this assignment to the declared outputs."""
    clause = []
    for leaf in leaves(outputs, []):
        if isinstance(leaf, IntVar):
            for value, lit in zip(leaf.values, leaf.lits):
                if lit in truth:
                    clause.append(-lit)
                    break
        elif isinstance(leaf, bool):
            continue
        elif isinstance(leaf, int):
            clause.append(-leaf if leaf in truth else leaf)
    return clause


def soft_units(direction, variable):
    """The soft units whose broken weight tracks the objective."""
    least, most = min(variable.values), max(variable.values)
    units = []
    for value, lit in zip(variable.values, variable.lits):
        weight = value - least if direction == "minimize" else most - value
        if weight > 0:
            # Breaking "not this value" costs the weight, and exactly one value
            # holds, so the total broken weight is the objective, shifted.
            units.append((-lit, weight))
    return units


def solve(request):
    """The child half: build, solve, and emit the whole protocol."""
    started = time.monotonic()
    sat, outputs, objective = load(request["instance"])
    limit = request["solution_limit"]

    from hermax.incremental import EvalMaxSATIncr

    solver = EvalMaxSATIncr()
    for clause in sat.clauses:
        if not clause:
            return finish("unsat", "the model contains an empty clause")
        solver.add_clause(list(clause))
    if objective is not None:
        for lit, weight in soft_units(objective[0], objective[1]):
            solver.add_soft_unit(lit, weight)

    optimum = None
    emitted = 0
    while emitted < limit:
        satisfiable = solver.solve()
        # SolveStatus is an IntEnum, and str() on one gives the number in
        # Python 3.11+, so the name is what to compare against.
        raw = solver.get_status()
        status = getattr(raw, "name", str(raw))
        spent = time.monotonic() - started
        if status == "ERROR":
            return finish("error", "the MaxSAT solver reported an error", solve_seconds=spent)
        if status in ("INTERRUPTED", "INTERRUPTED_SAT", "UNKNOWN"):
            return finish("timeout", "the optimum was not proven", solve_seconds=spent)
        if status == "UNSAT" or not satisfiable:
            return finish("complete" if emitted else "unsat", solve_seconds=spent)
        if status != "OPTIMUM":
            return finish("timeout", f"unexpected solver status {status}", solve_seconds=spent)

        cost = solver.get_cost()
        if optimum is None:
            optimum = cost
        elif cost > optimum:
            # Every remaining answer is worse, so the optimal ones are exhausted.
            return finish("complete", solve_seconds=spent)

        truth = {lit for lit in range(1, solver.num_vars + 1) if solver.val(lit) > 0}
        emit({"type": "solution", "values": render(outputs, truth)})
        emitted += 1
        if emitted >= limit:
            break
        clause = blocking_clause(outputs, truth)
        if not clause:
            return finish("complete", solve_seconds=time.monotonic() - started)
        solver.add_clause(clause)
    finish("limit", solve_seconds=time.monotonic() - started)


def supervise(request):
    """The parent half: run the child under the budget and kill it if it runs over."""
    try:
        result = subprocess.run([sys.executable, "/opt/runner/run.py", "--solve"],
                                stdin=subprocess.DEVNULL, stderr=sys.stderr,
                                timeout=request["execution_timeout"])
    except subprocess.TimeoutExpired:
        # The child streamed any solutions it found straight to this stdout; all
        # that is missing is the final status it never reached.
        return finish("timeout", "the MaxSAT search exceeded its budget")
    if result.returncode:
        return finish("error", f"the solver process exited {result.returncode}")


def main():
    request = json.loads(Path("/input/request.json").read_text())
    if request.get("legacy"):
        return finish("unsupported", "This integration has no legacy submission format")
    if "--solve" in sys.argv:
        return solve(request)
    supervise(request)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
