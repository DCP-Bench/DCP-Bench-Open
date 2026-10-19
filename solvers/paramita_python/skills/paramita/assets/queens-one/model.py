import sys

from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf
from paramita.solvers import SatSolver

# Usage: python3 model.py [n]
# Places n queens on an n x n board so that none attack each other; prints one placement.
n = int(sys.argv[1]) if len(sys.argv) > 1 else 8

# q[r][c] is true when a queen stands on row r, column c.
q = [[Bool(f"q_{r}_{c}") for c in range(n)] for r in range(n)]
constraints = []
constraints += [sum(q[r]) == 1 for r in range(n)]                        # one queen per row
constraints += [sum(q[r][c] for r in range(n)) == 1 for c in range(n)]   # one queen per column
for d in range(-(n - 1), n):                                             # diagonals r - c = d
    cells = [q[r][r - d] for r in range(n) if 0 <= r - d < n]
    if len(cells) > 1:
        constraints.append(sum(cells) <= 1)
for s_ in range(2 * n - 1):                                              # anti-diagonals r + c = s
    cells = [q[r][s_ - r] for r in range(n) if 0 <= s_ - r < n]
    if len(cells) > 1:
        constraints.append(sum(cells) <= 1)

pool = DimacsVariablePool()
solver = SatSolver.from_name("Cadical300")
for e in constraints:
    add_to_container(e, to_cnf, solver, pool)

if not solver.solve():
    print("unsatisfiable")
else:
    true = {abs(lit) for lit in solver.model() if lit > 0}
    for r in range(n):
        print("".join("Q" if pool.get_variable(q[r][c]) in true else "." for c in range(n)))
    print(f"Queens placed: {n}")
