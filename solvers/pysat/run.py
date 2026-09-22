"""Runner protocol for the pysat integration. Runs inside the image only.

A submission defines `build(instance)` returning `(cnf, outputs)`, where `cnf`
is a `pysat.formula.CNF` and `outputs` maps each declared output name to a
literal, a `pysat.integer.Integer`, a plain bool, or nested lists of those.

The submission builds that CNF with PySAT's own tools: `IDPool` for variable
identifiers, `CardEnc` and `PBEnc` for cardinality and pseudo-Boolean
constraints, and `IntegerEngine` plus `Integer` for finite-domain variables,
whose `clausify()` returns the CNF to hand over.

PySAT solves satisfaction problems and nothing else, which is why the metadata
declares `optimization: false`. A submission that hands back an objective is
told so rather than being solved as if the objective were not there.

The search runs inside a C extension, so a Python signal handler cannot fire
while it is running. The budget is therefore enforced with PySAT's own
interrupt, driven from a timer thread; the SIGALRM below only covers the pure
Python phase where the submission builds its clauses.

Enumeration blocks the previous **declared outputs**, not the whole assignment:
two models of the same CNF routinely agree on everything the problem declares,
and the evaluator counts distinct declared outputs.
"""
import contextlib
import importlib.util
import json
from pathlib import Path
import signal
import sys
import threading
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish  # noqa: E402

from pysat.formula import CNF  # noqa: E402
from pysat.integer import Integer  # noqa: E402

# Glucose rather than CaDiCaL: PySAT raises NotImplementedError for
# "limited solve" on CaDiCaL and Lingeling, so those two cannot be stopped
# mid-search and would run until the evaluator killed the container.
SOLVER_NAME = "glucose42"

# How far ahead of the hard SIGALRM deadline the solver is interrupted, so the
# runner reports its own timeout rather than losing a race to the signal.
INTERRUPT_MARGIN = 0.5


def load(instance):
    spec = importlib.util.spec_from_file_location("candidate", "/input/model.py")
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        result = module.build(instance)
    if not isinstance(result, tuple) or len(result) not in (2, 3):
        raise ValueError("build(instance) must return (cnf, outputs)")
    # A third element is an objective. PySAT solves satisfaction problems only,
    # so an objective is refused here rather than quietly dropped, which would
    # let a merely feasible answer pass as an optimal one.
    objective = result[2] if len(result) == 3 else None
    cnf, outputs = result[0], result[1]
    if not isinstance(cnf, CNF):
        raise ValueError("the first value must be a pysat.formula.CNF; an "
                         "IntegerEngine gives one back from clausify()")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return a nonempty output dictionary")
    return cnf, outputs, objective


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


def render(node, model, truth):
    if isinstance(node, dict):
        return {name: render(value, model, truth) for name, value in node.items()}
    if isinstance(node, (list, tuple)):
        return [render(value, model, truth) for value in node]
    if isinstance(node, Integer):
        return node.decode(model)
    if isinstance(node, bool):
        return node
    if isinstance(node, int):
        # A literal from the model's pool, rather than a constant it fixed.
        return node in truth
    raise ValueError("an output leaf must be an Integer, a literal, an int or a "
                     f"bool; got {type(node).__name__}")


def blocking_clause(outputs, model, truth):
    """Rule out exactly this assignment to the declared outputs."""
    clause = []
    for leaf in leaves(outputs, []):
        if isinstance(leaf, Integer):
            # `equals(v)` is the literal for "this variable takes v", so
            # forbidding the value it took is enough to change the answer.
            clause.append(-leaf.equals(leaf.decode(model)))
        elif isinstance(leaf, bool):
            continue
        elif isinstance(leaf, int):
            clause.append(-leaf if leaf in truth else leaf)
    return clause


def main():
    request = json.loads(Path("/input/request.json").read_text())
    if request.get("legacy"):
        return finish("unsupported", "This integration has no legacy submission format")

    def expired(signum, frame):
        raise TimeoutError("Runner execution budget exceeded")

    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, request["execution_timeout"])

    started = time.monotonic()
    cnf, outputs, objective = load(request["instance"])
    if objective is not None:
        return finish("unsupported", "PySAT solves satisfaction problems only; this problem has an objective")
    limit = request["solution_limit"]

    from pysat.solvers import Solver

    emitted = 0
    with Solver(name=SOLVER_NAME, bootstrap_with=cnf) as solver:
        while emitted < limit:
            left = request["execution_timeout"] - (time.monotonic() - started)
            if left <= 0:
                return finish("timeout", solve_seconds=time.monotonic() - started)
            # The search runs inside a C extension, so the SIGALRM above cannot
            # fire until it returns. PySAT's own interrupt is what actually
            # stops it, and without this the container runs until the evaluator
            # kills it from outside rather than reporting its own timeout.
            #
            # The interrupt is pulled forward by a margin so it always lands
            # before the SIGALRM. Armed for the same instant, the two race, and
            # a SIGALRM that wins surfaces as `execution_error` rather than the
            # `timeout` the runner is supposed to report for itself.
            alarm = threading.Timer(max(left - INTERRUPT_MARGIN, 0.01), solver.interrupt)
            alarm.start()
            try:
                answer = solver.solve_limited(expect_interrupt=True)
            finally:
                alarm.cancel()
                solver.clear_interrupt()
            if answer is None:
                return finish("timeout", solve_seconds=time.monotonic() - started)
            if not answer:
                spent = time.monotonic() - started
                return finish("complete" if emitted else "unsat", solve_seconds=spent)
            model = solver.get_model()
            truth = {lit for lit in model if lit > 0}
            emit({"type": "solution", "values": render(outputs, model, truth)})
            emitted += 1
            if emitted >= limit:
                break
            clause = blocking_clause(outputs, model, truth)
            if not clause:
                # Nothing the problem declares can differ, so there is no second
                # answer to look for.
                return finish("complete", solve_seconds=time.monotonic() - started)
            solver.add_clause(clause)
    finish("limit", solve_seconds=time.monotonic() - started)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
