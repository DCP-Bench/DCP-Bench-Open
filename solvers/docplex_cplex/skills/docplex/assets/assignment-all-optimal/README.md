# Assignment (all optimal solutions)

**Problem:** assign 3 workers to 3 tasks, one each, at minimum total cost, listing every optimal assignment.
**Shows:** `binary_var_matrix` keyed by (row, column), minimise with `mipgap = 0` and the optimum accepted only on `integer optimal solution`, re-posting the optimum as a constraint, no-good enumeration over the assignment binaries that is complete only when it ends on `integer infeasible`.
**Run:** `python3 model.py`
**Expected:** `Optimal cost: 5`
**Expected:** `Optimal assignments: 2`
