"""Pick projects within a budget, maximising total value, with pairwise conflicts.

Usage: python model.py [data.json]
The data is read with Python's standard json module (nothing to install). Every size
comes from the data, the ragged list `conflicts` becomes a predicate, and keys the
model does not use ("name", "note") are ignored.
"""
import json
import sys

from idp_engine import IDP, Theory

path = sys.argv[1] if len(sys.argv) > 1 else "data.json"
with open(path) as f:
    data = json.load(f)

value, cost, budget = data["value"], data["cost"], data["budget"]
conflicts = data["conflicts"]          # ragged: conflicts[i] lists the projects that clash with i
n = len(value)

KB = """
vocabulary V {
    type Project <: Int
    budget: () -> Int
    value: Project -> Int
    cost: Project -> Int
    clash: Project * Project -> Bool
    take: Project -> Bool
    profit: () -> Int
}
theory T: V {
    // stay within the budget
    sum{{ cost(p) | p in Project: take(p) }} =< budget().
    // two clashing projects are never both taken
    ! p, q in Project: clash(p, q) => ~(take(p) & take(q)).
    // the objective
    profit() = sum{{ value(p) | p in Project: take(p) }}.
}
"""


def fo_map(values):
    """{0->a, 1->b, ...} for a 1-D list."""
    return "{" + ", ".join(f"{i}->{v}" for i, v in enumerate(values)) + "}"


def fo_set(pairs):
    """The set of true tuples of a predicate; {} when there is none."""
    return "{" + ", ".join(f"({a},{b})" for a, b in pairs) + "}"


structure = f"""
structure S: V {{
    Project := {{0..{n - 1}}}.
    budget := {budget}.
    value := {fo_map(value)}.
    cost := {fo_map(cost)}.
    clash := {fo_set((i, j) for i, row in enumerate(conflicts) for j in row)}.
}}
"""

kb = IDP.from_str(KB + structure)
theory = Theory(*kb.get_blocks("T, S"))
theory.optimize("profit()", minimize=False)   # raises AssertionError if nothing is feasible
for model in theory.expand(max=1, timeout_seconds=0):
    if isinstance(model, str):
        continue
    chosen = [p for p in range(n) if str(model[f"take({p})"].value) == "true"]
    print(f"Maximum value: {model['profit()'].value}")
    print(f"Projects: {chosen}")
