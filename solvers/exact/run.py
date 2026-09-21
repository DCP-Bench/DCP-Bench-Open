"""Runner protocol for the exact integration. Runs inside the image only.

A submission defines `build(instance)` returning `(pb, outputs)`, where `pb` is
the `Pb` builder from `dcp_pb` and `outputs` maps each declared output name to a
`Var`, a plain int or bool, or nested lists of those. An objective is declared
on the builder with `pb.minimise(terms)` or `pb.maximise(terms)` rather than
returned, because Exact takes a linear expression directly and needs no
auxiliary variable to hold it.

Exact bounds its own search: `toOptimum` and `runFull` both take a timeout, and
`toOptimum` reports whether it reached the optimum or ran out of time. So unlike
the MaxSAT integration here, no child process is needed.

Optimality is reported only when Exact says it proved it. Enumeration fixes the
objective at that optimum first, so every further answer is optimal too.
"""
import contextlib
import importlib.util
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish  # noqa: E402

from dcp_pb import Pb, Var  # noqa: E402


def load(instance):
    spec = importlib.util.spec_from_file_location("candidate", "/input/model.py")
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        result = module.build(instance)
    if not isinstance(result, tuple) or len(result) != 2:
        raise ValueError("build(instance) must return (pb, outputs)")
    pb, outputs = result
    if not isinstance(pb, Pb):
        raise ValueError("the first value must be the Pb builder from dcp_pb")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return a nonempty output dictionary")
    return pb, outputs


def leaves(node, found):
    if isinstance(node, dict):
        for value in node.values():
            leaves(value, found)
    elif isinstance(node, (list, tuple)):
        for value in node:
            leaves(value, found)
    elif isinstance(node, Var):
        found.append(node)
    return found


def render(node, values):
    if isinstance(node, dict):
        return {name: render(value, values) for name, value in node.items()}
    if isinstance(node, (list, tuple)):
        return [render(value, values) for value in node]
    if isinstance(node, Var):
        value = values[node.name]
        return bool(value) if node.boolean else value
    if isinstance(node, (bool, int)):
        return node
    raise ValueError(f"an output leaf must be a Var, an int or a bool; got {type(node).__name__}")


def read(pb, outputs):
    """The value of every declared output variable in the last solution."""
    names = [var.name for var in leaves(outputs, [])]
    if not names:
        return {}
    return dict(zip(names, pb.solver.getLastSolutionFor(names)))


def block(pb, outputs, values):
    """Forbid exactly this assignment of the declared outputs.

    Each output is pinned to its value by an indicator, and at least one of them
    has to come out false next time.
    """
    flags = [pb.is_value(var, values[var.name]) for var in leaves(outputs, [])]
    if not flags:
        return False
    pb.le([(1, flag) for flag in flags], len(flags) - 1)
    return True


def main():
    request = json.loads(Path("/input/request.json").read_text())
    if request.get("legacy"):
        return finish("unsupported", "This integration has no legacy submission format")

    started = time.monotonic()
    pb, outputs = load(request["instance"])
    limit = request["solution_limit"]
    budget = request["execution_timeout"]

    def left():
        return budget - (time.monotonic() - started)

    if pb.objective is not None:
        terms, minimise = pb.objective
        pb.solver.setObjective(Pb._terms(terms), minimise)
        if left() <= 0:
            return finish("timeout", solve_seconds=time.monotonic() - started)
        state, optimum = pb.solver.toOptimum(left())
        spent = time.monotonic() - started
        if state == "UNSAT":
            return finish("unsat", solve_seconds=spent)
        if state != "SAT":
            # "SAT" from toOptimum means the optimum was proven; "TIMEOUT" means
            # the search stopped short. Exact still has a solution in hand then,
            # so reporting anything but SAT as an answer would pass off an
            # unproven one as optimal.
            return finish("timeout", f"the optimum was not proven ({state})", solve_seconds=spent)
        # Exact minimises internally, so a maximisation comes back negated.
        # Hold the objective there, and anything found from here on is optimal.
        pb.eq(terms, optimum if minimise else -optimum)

    emitted = 0
    while emitted < limit:
        if left() <= 0:
            return finish("timeout", solve_seconds=time.monotonic() - started)
        state = pb.solver.runFull(False, left())
        spent = time.monotonic() - started
        if state == "UNSAT":
            return finish("complete" if emitted else "unsat", solve_seconds=spent)
        if state != "SAT":
            return finish("timeout", f"search stopped as {state}", solve_seconds=spent)
        values = read(pb, outputs)
        emit({"type": "solution", "values": render(outputs, values)})
        emitted += 1
        if emitted >= limit:
            break
        if not block(pb, outputs, values):
            return finish("complete", solve_seconds=time.monotonic() - started)
    finish("limit", solve_seconds=time.monotonic() - started)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
