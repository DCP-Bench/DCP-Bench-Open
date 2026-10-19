# Pigeonhole (infeasible)

**Problem:** place 4 pigeons in 3 holes with at most one pigeon per hole.
**Shows:** what "no solution" looks like: Savile Row exits 0, prints no `letting` lines and writes no solution file; the info file (`model.eprime.info` when there is no parameter file) has `SolverSatisfiable:0`, and `SolverTimeOut:0` says the search finished, so infeasibility is proven.
**Run:** `savilerow model.eprime -run-solver -solutions-to-stdout && grep -E 'SolverSatisfiable|SolverTimeOut' model.eprime.info`
**Expected:** `SolverSatisfiable:0`
**Expected:** `SolverTimeOut:0`
