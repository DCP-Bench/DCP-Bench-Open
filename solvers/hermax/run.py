"""Runner protocol for the hermax integration. Runs inside the image only.

A submission defines `build(instance)` returning `(model, outputs)`, where
`model` is a `hermax.model.Model` and `outputs` maps each declared output name
to variables of that model.

**The objective goes on the model, not into the return.** A MaxSAT solver
minimises the weight of the soft clauses it breaks, so an objective is written
the way hermax writes one -- `model.obj[weight] += literal`, which pays
`weight` when the literal is false. Maximising a quantity means paying for its
complement. The runner only needs to know an objective exists, which it reads
off `result.cost`: hermax leaves that None for a model with no soft clauses.

Routing an objective through an auxiliary integer variable instead, with
`sum(...) == total`, is what the earlier version of this integration did and it
is a trap: on a four-by-four assignment problem, encoding that one equality
took 43 seconds against 3 seconds to solve the whole model with soft clauses.

Optimality is reported only on the `optimum` status. `interrupted_sat` means a
solution was found without proving it best, which is a timeout here rather than
an answer, because the evaluator would otherwise compare it against the
reference optimum as if it were one.
"""
import contextlib
import functools
import importlib.util
import json
import operator
from pathlib import Path
import sys
import time

sys.path.insert(0, "/opt/runner")
from runtime import emit, finish, mapped  # noqa: E402

from hermax.model import BoolMatrix, IntMatrix, IntVar, Literal, Model  # noqa: E402

# `ok` on a SolveResult also covers interrupted_sat, which is not an answer here.
ANSWERED = ("sat", "optimum")
UNPROVEN = ("interrupted", "interrupted_sat", "unknown")


def load(instance):
    """Import the submission and normalise what it returned."""
    spec = importlib.util.spec_from_file_location("candidate", "/input/model.py")
    module = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)
        returned = module.build(instance)
    if not isinstance(returned, tuple) or len(returned) != 2:
        raise ValueError("build(instance) must return (model, outputs), with any "
                         "objective declared on model.obj")
    model, outputs = returned
    if not isinstance(model, Model):
        raise ValueError("the first value must be a hermax.model.Model")
    if not isinstance(outputs, dict) or not outputs:
        raise ValueError("build(instance) must return a nonempty output dictionary")
    return model, outputs


def atoms(node, found):
    """Every individual variable under the declared outputs, for blocking."""
    if isinstance(node, dict):
        for value in node.values():
            atoms(value, found)
    elif isinstance(node, (BoolMatrix, IntMatrix)):
        atoms(list(node.flatten()), found)
    elif isinstance(node, (list, tuple)) or hasattr(node, "__iter__"):
        for value in node:
            atoms(value, found)
    else:
        found.append(node)
    return found


def blocking_clause(outputs, result):
    """Rule out exactly this assignment to the declared outputs."""
    disjuncts = []
    for leaf in atoms(outputs, []):
        value = result[leaf]
        if isinstance(leaf, IntVar):
            disjuncts.append(leaf != value)
        elif isinstance(leaf, Literal):
            disjuncts.append(~leaf if value else leaf)
        else:
            raise ValueError("an output leaf must be an IntVar or a Literal; got "
                             f"{type(leaf).__name__}")
    if not disjuncts:
        return None
    return functools.reduce(operator.or_, disjuncts)


def main():
    request = json.loads(Path("/input/request.json").read_text())
    if request.get("legacy"):
        return finish("unsupported", "This integration has no legacy submission format")

    started = time.monotonic()
    deadline = started + request["execution_timeout"]
    model, outputs = load(request["instance"])

    limit = request["solution_limit"]
    best = None
    emitted = 0
    while emitted < limit:
        left = deadline - time.monotonic()
        if left <= 0:
            return finish("timeout", "the budget ran out before the search finished",
                          solve_seconds=time.monotonic() - started)
        result = model.solve(time_limit=left)
        spent = time.monotonic() - started
        status = result.status
        if status == "error":
            return finish("error", "the MaxSAT solver reported an error", solve_seconds=spent)
        if status in UNPROVEN:
            detail = ("the optimum was not proven" if result.cost is not None
                      else "the search did not finish")
            return finish("timeout", detail, solve_seconds=spent)
        if status == "unsat":
            return finish("complete" if emitted else "unsat", solve_seconds=spent)
        if status not in ANSWERED:
            return finish("error", f"unexpected solver status {status}", solve_seconds=spent)
        # hermax leaves cost None when the model declares no soft clauses.
        if result.cost is not None:
            if best is None:
                best = result.cost
            elif result.cost > best:
                # Every remaining answer is worse, so the optimal ones are done.
                return finish("complete", solve_seconds=spent)

        emit({"type": "solution", "values": mapped(outputs, lambda v: result[v])})
        emitted += 1
        if emitted >= limit:
            break
        clause = blocking_clause(outputs, result)
        if clause is None:
            return finish("complete", solve_seconds=time.monotonic() - started)
        model &= clause
    finish("limit", solve_seconds=time.monotonic() - started)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        import traceback
        traceback.print_exc(file=sys.stderr)
        finish("error", str(error))
