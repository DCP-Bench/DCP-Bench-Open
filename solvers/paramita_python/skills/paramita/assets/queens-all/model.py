from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf
from paramita.solvers import SatSolver

# Enumerates every placement of 6 queens. The blocking clause covers the cell
# variables only, which are the answer variables, so each board is counted once.
n = 6

q = [[Bool(f"q_{r}_{c}") for c in range(n)] for r in range(n)]
constraints = []
constraints += [sum(q[r]) == 1 for r in range(n)]
constraints += [sum(q[r][c] for r in range(n)) == 1 for c in range(n)]
for d in range(-(n - 1), n):
    cells = [q[r][r - d] for r in range(n) if 0 <= r - d < n]
    if len(cells) > 1:
        constraints.append(sum(cells) <= 1)
for s_ in range(2 * n - 1):
    cells = [q[r][s_ - r] for r in range(n) if 0 <= s_ - r < n]
    if len(cells) > 1:
        constraints.append(sum(cells) <= 1)

pool = DimacsVariablePool()
solver = SatSolver.from_name("Cadical300")
for e in constraints:
    add_to_container(e, to_cnf, solver, pool)
cells = [pool.get_variable(q[r][c]) for r in range(n) for c in range(n)]

count = 0
while solver.solve():
    true = {abs(lit) for lit in solver.model() if lit > 0}
    count += 1
    # Rule out exactly this placement: some cell must differ from it.
    solver.add_clause([-v if v in true else v for v in cells])
print(f"Solutions: {count}")
