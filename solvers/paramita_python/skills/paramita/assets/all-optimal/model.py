from paramita.modelling import Bool, DimacsVariablePool, add_to_container, add_to_weighted_container, to_cnf
from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver, SatSolver

# All optimal selections of a knapsack with ties: solve for the optimum, then
# add the hard constraint "objective == optimum" to a fresh solver and enumerate.
weights = [2, 2, 2, 4]
values = [3, 3, 3, 6]
capacity = 4

take = [Bool(f"take_{i}") for i in range(len(weights))]
subject_to = sum(w * t for w, t in zip(weights, take)) <= capacity
objective = sum(v * t for v, t in zip(values, take))

pool = DimacsVariablePool()
maxsat = MaxSatSolver.from_name("EvalMaxSAT2022")
constant = add_to_weighted_container(objective, subject_to, to_cnf, maxsat, pool)
if maxsat.solve() != MAXSAT_ANSWER.OPTIMAL:
    raise SystemExit("optimum not proven")
best = constant + maxsat.benefit()
print(f"Optimum: {best}")

pool2 = DimacsVariablePool()
solver = SatSolver.from_name("Cadical300")
for e in [subject_to, objective == best]:
    add_to_container(e, to_cnf, solver, pool2)
ids = [pool2.get_variable(t) for t in take]

count = 0
while solver.solve():
    true = {abs(lit) for lit in solver.model() if lit > 0}
    count += 1
    print("selection:", [i for i, v in enumerate(ids) if v in true])
    solver.add_clause([-v if v in true else v for v in ids])
print(f"All optimal solutions: {count}")
