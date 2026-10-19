# All solutions of n-queens: solve, forbid the solution found with a no-good, solve again.
import sys

from pyscipopt import Model, quicksum

n = int(sys.argv[1]) if len(sys.argv) > 1 else 6

m = Model("queens-all")
m.hideOutput()
b = {(r, c): m.addVar(vtype="B", name=f"b_{r}_{c}") for r in range(n) for c in range(n)}
for i in range(n):
    m.addCons(quicksum(b[i, c] for c in range(n)) == 1)
    m.addCons(quicksum(b[r, i] for r in range(n)) == 1)
for d in range(-n + 1, n):
    m.addCons(quicksum(b[r, r - d] for r in range(n) if 0 <= r - d < n) <= 1)
    m.addCons(quicksum(b[r, d + n - 1 - r] for r in range(n) if 0 <= d + n - 1 - r < n) <= 1)

solutions = []
while True:
    m.optimize()
    status = m.getStatus()
    if status == "infeasible":      # no further solution: the enumeration is complete
        break
    if status != "optimal":         # any other status: the list would be incomplete
        raise SystemExit(f"Stopped early: {status}")
    ones = [v for v in b.values() if m.getVal(v) > 0.5]
    zeros = [v for v in b.values() if m.getVal(v) <= 0.5]
    solutions.append([c + 1 for r in range(n) for c in range(n) if m.getVal(b[r, c]) > 0.5])
    m.freeTransform()  # required before changing a solved model
    # no-good: at least one binary must flip
    m.addCons(quicksum(1 - v for v in ones) + quicksum(zeros) >= 1)

print("Last status:", m.getStatus())
for s in solutions:
    print(s)
print("Solutions:", len(solutions))
