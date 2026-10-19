from paramita.modelling import Bool, DimacsVariablePool, add_to_weighted_container, to_cnf
from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

# 0/1 knapsack: maximise the total value under a weight capacity.
weights = [3, 4, 2]
values = [30, 50, 40]
capacity = 7

take = [Bool(f"take_{i}") for i in range(len(weights))]
subject_to = sum(w * t for w, t in zip(weights, take)) <= capacity
objective = sum(v * t for v, t in zip(values, take))

pool = DimacsVariablePool()
maxsat = MaxSatSolver.from_name("EvalMaxSAT2022")
# Maximises `objective`; the return value is its constant part.
constant = add_to_weighted_container(objective, subject_to, to_cnf, maxsat, pool)
answer = maxsat.solve()

if answer != MAXSAT_ANSWER.OPTIMAL:
    print(f"not proven optimal: {answer}")
else:
    best = constant + maxsat.benefit()
    chosen = {abs(lit) for lit in maxsat.model() if lit > 0}
    picked = [i for i, t in enumerate(take) if pool.get_variable(t) in chosen]
    print(f"Optimum: {best}")
    print(f"Items: {picked}")
