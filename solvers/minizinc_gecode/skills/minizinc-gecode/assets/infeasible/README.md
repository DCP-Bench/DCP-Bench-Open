# Pigeonhole (infeasible)

**Problem:** place 4 pigeons in 3 holes with at most one pigeon per hole.
**Shows:** a model with no solution, the `=====UNSATISFIABLE=====` marker, the `include "globals.mzn"` line that `all_different` needs.
**Run:** `minizinc --solver gecode model.mzn`
**Expected:** `=====UNSATISFIABLE=====`
