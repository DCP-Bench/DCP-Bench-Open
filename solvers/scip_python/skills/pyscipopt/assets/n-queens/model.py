# n-queens: place n queens on an n x n board so that no two attack each other.
import sys

from pyscipopt import Model, quicksum

n = int(sys.argv[1]) if len(sys.argv) > 1 else 8

m = Model("queens")
m.hideOutput()
# one-hot encoding: b[r, c] == 1 when the queen of row r stands in column c
b = {(r, c): m.addVar(vtype="B", name=f"b_{r}_{c}") for r in range(n) for c in range(n)}
# one queen per row and per column
for i in range(n):
    m.addCons(quicksum(b[i, c] for c in range(n)) == 1)
    m.addCons(quicksum(b[r, i] for r in range(n)) == 1)
# at most one queen per diagonal and per anti-diagonal
for d in range(-n + 1, n):
    m.addCons(quicksum(b[r, r - d] for r in range(n) if 0 <= r - d < n) <= 1)
    m.addCons(quicksum(b[r, d + n - 1 - r] for r in range(n) if 0 <= d + n - 1 - r < n) <= 1)
# no objective: a satisfaction problem

m.optimize()
status = m.getStatus()
print("Status:", status)
if status == "optimal":  # with no objective, "optimal" means a solution was found
    sol = m.getBestSol()
    # the column of each row's queen, numbered from 1, evaluated as an expression
    queens = [round(sol[quicksum((c + 1) * b[r, c] for c in range(n))]) for r in range(n)]
    print("Queens:", queens)
