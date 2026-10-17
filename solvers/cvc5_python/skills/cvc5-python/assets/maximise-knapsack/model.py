"""Maximise: 0/1 knapsack, read from a JSON file (default data.json).

Shows: Boolean decision variables, weighted sums with Sum(If(...)),
optimisation by tightening (cvc5 has no optimiser), proof by unsat.
"""
import json
import sys

from cvc5.pythonic import *

path = sys.argv[1] if len(sys.argv) > 1 else "data.json"
with open(path) as f:
    data = json.load(f)
values, weights, capacity = data["values"], data["weights"], data["capacity"]
n = len(values)

take = Bools([f"take_{i}" for i in range(n)])
value = Sum([If(take[i], values[i], 0) for i in range(n)])
weight = Sum([If(take[i], weights[i], 0) for i in range(n)])

s = SolverFor("QF_LIA")
s.add(weight <= capacity)

best, chosen = None, None
while True:
    result = s.check()
    if result != sat:
        break
    m = s.model()
    best = m.eval(value, model_completion=True).as_long()
    chosen = [i for i in range(n) if is_true(m.eval(take[i], model_completion=True))]
    s.add(value > best)  # demand a strictly better solution

if result == unknown:
    print(f"undecided: {s.reason_unknown()}; best so far {best}")
elif best is None:
    print("infeasible")
else:
    # the last check returned unsat, so no solution better than `best` exists
    print(f"Optimal value: {best}")
    print(f"Items: {chosen}")
