"""Routing: shortest closed tour through all cities, read from a JSON file
(default data.json, a symmetric distance matrix under "dist").

Shows:
- successor variables: succ[i] is the next city, Distinct makes a permutation
- subtour elimination with position variables (Miller-Tucker-Zemlin style):
  Implies(succ[i] == j, pos[j] == pos[i] + 1) for cities j, i other than 0
- cost by enumeration: a sum over j of If(succ[i] == j, dist[i][j], 0)
- minimisation by tightening until unsat
"""
import json
import sys

from cvc5.pythonic import *

path = sys.argv[1] if len(sys.argv) > 1 else "data.json"
with open(path) as f:
    dist = json.load(f)["dist"]
n = len(dist)

succ = [Int(f"succ_{i}") for i in range(n)]
pos = [Int(f"pos_{i}") for i in range(n)]

s = SolverFor("QF_LIA")
for i in range(n):
    s.add(succ[i] >= 0, succ[i] < n, succ[i] != i)
    s.add(pos[i] >= 0, pos[i] < n)
s.add(Distinct(succ))
s.add(pos[0] == 0)
for i in range(1, n):
    for j in range(1, n):
        if i != j:
            s.add(Implies(succ[i] == j, pos[j] == pos[i] + 1))

legs = [Sum([If(succ[i] == j, dist[i][j], 0) for j in range(n)]) for i in range(n)]
total = Sum(legs)

best, best_succ = None, None
while True:
    result = s.check()
    if result != sat:
        break
    m = s.model()
    best = m.eval(total, model_completion=True).as_long()
    best_succ = [m.eval(v, model_completion=True).as_long() for v in succ]
    s.add(total < best)

if result == unknown:
    print(f"undecided: {s.reason_unknown()}; best so far {best}")
else:
    tour, city = [0], 0
    for _ in range(n - 1):
        city = best_succ[city]
        tour.append(city)
    print(f"Optimal tour length: {best}")
    print("tour:", tour + [0])
