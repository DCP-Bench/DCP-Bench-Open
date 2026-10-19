# Knapsack (maximise)

**Problem:** 0/1 knapsack with 4 items and capacity 10.
**Shows:** matrix `given`s from a parameter file, a Boolean matrix used as 0/1 in a weighted sum, an objective variable whose domain is bounded by the data (`int(0..sum(values))`), `maximising`, each quantified `sum` in parentheses, and the proof check: `$ Minion SolverTimeOut: 0` in the solution header (or `SolverTimeOut:0` in `knapsack.param.info`) means the optimum is proven.
**Run:** `savilerow knapsack.eprime knapsack.param -run-solver -solutions-to-stdout`
**Expected:** `letting take be [false, true, false, true]`
**Expected:** `letting total be 90`
**Expected:** `$ Minion SolverTimeOut: 0`
