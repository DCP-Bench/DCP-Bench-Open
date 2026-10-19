from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf
from paramita.solvers import SatSolver

# Pigeonhole: 3 pigeons, 2 holes, every pigeon in a hole, at most one pigeon per hole.
pigeons, holes = 3, 2
x = [[Bool(f"x_{p}_{h}") for h in range(holes)] for p in range(pigeons)]
constraints = [sum(x[p]) == 1 for p in range(pigeons)]
constraints += [sum(x[p][h] for p in range(pigeons)) <= 1 for h in range(holes)]

pool = DimacsVariablePool()
solver = SatSolver.from_name("Cadical300")
for e in constraints:
    add_to_container(e, to_cnf, solver, pool)

result = solver.solve()
print("status: satisfiable" if result else "status: unsatisfiable")
