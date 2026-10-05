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

An output may also be a linear expression of the model's variables, which is
how a value too wide for one `IntVar` is declared: hermax encodes an IntVar
with one literal per value, so an IntVar over a ten-digit range exhausts memory
by itself, while `sum(10**(9-i) * digit[i])` over 0..9 IntVars or
`sum(2**k * bit[k])` over Booleans does not. Such a sum is hermax's own
`PBExpr` (a single weighted literal is a `Term`); `result[...]` cannot decode
either, so the runner adds up the decoded terms itself, and when enumerating it
blocks the literals and variables the expression sums. Another combination of
those can reach the same total, so a declared output equal to one already
reported is skipped rather than emitted twice.
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

from hermax.model import (BoolMatrix, IntMatrix, IntVar, Literal, Model,  # noqa: E402
                          PBExpr, Term)

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


def summed(expression):
    """The weighted literals and derived integers a PBExpr or Term adds up."""
    if isinstance(expression, Term):
        return [(expression.coefficient, expression.literal)], 0
    return ([(term.coefficient, term.literal) for term in expression.terms]
            + list(expression.int_terms), expression.constant)


def read(leaf, result):
    """The value of one declared output under a solve result.

    hermax decodes variables and containers itself; a PBExpr or Term is summed
    here from its decoded terms, since `result[expression]` raises TypeError.
    """
    if not isinstance(leaf, (PBExpr, Term)):
        return result[leaf]
    pairs, total = summed(leaf)
    for coefficient, item in pairs:
        if isinstance(coefficient, bool) or not isinstance(coefficient, int):
            raise ValueError("an output expression must have integer coefficients; got "
                             f"{coefficient!r}")
        total += coefficient * int(result[item])
    return total


def blocking_clause(outputs, result):
    """Rule out exactly this assignment to the declared outputs.

    For an expression output, that means this assignment to every literal and
    variable it sums, not this total: a total cannot be forbidden by a clause.
    """
    disjuncts = []
    for leaf in atoms(outputs, []):
        if isinstance(leaf, (PBExpr, Term)):
            items = [item for _, item in summed(leaf)[0]]
        elif isinstance(leaf, (IntVar, Literal)):
            items = [leaf]
        else:
            raise ValueError("an output leaf must be an IntVar, a Literal, or a linear "
                             f"expression of them; got {type(leaf).__name__}")
        for item in items:
            value = result[item]
            if isinstance(item, Literal):
                disjuncts.append(~item if value else item)
                continue
            different = item != value
            if not isinstance(different, Literal):
                # A derived integer such as x // 3 compares to a PB constraint,
                # which hermax cannot put in a clause.
                raise ValueError("an output expression can only be enumerated over "
                                 "literals and integer variables; got "
                                 f"{type(item).__name__}")
            disjuncts.append(different)
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
    # Declared outputs already reported; see blocking_clause on expressions.
    seen = set()
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

        values = mapped(outputs, lambda leaf: read(leaf, result))
        key = json.dumps(values, sort_keys=True)
        if key not in seen:
            seen.add(key)
            emit({"type": "solution", "values": values})
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
