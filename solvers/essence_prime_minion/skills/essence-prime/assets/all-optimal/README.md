# Knapsack with ties (all optimal solutions)

**Problem:** list every selection of a 5-item knapsack (weights and values 1..5, capacity 6) that reaches the best value.
**Shows:** the two-pass pattern in a shell script. Pass 1 adds `find best` with `maximising best` and `best = (EXPR)` so the optimum of an objective *expression* can be read, and checks `SolverTimeOut:0`. Pass 2 deletes the objective line (`-all-solutions` is ignored on an optimisation model), appends `(EXPR) = optimum` after the last constraint, and enumerates with `-all-solutions -S0`.
**Run:** `sh all-optimal.sh`
**Expected:** `optimum: 6`
**Expected:** `optimal solutions: 3`
