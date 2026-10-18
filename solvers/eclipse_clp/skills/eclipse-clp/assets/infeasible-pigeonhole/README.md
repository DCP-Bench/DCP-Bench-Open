# Pigeonhole (infeasible)

**Problem:** 9 pigeons in 8 holes, no two in the same hole.
**Shows:** an infeasible model. When the search is exhausted the goal fails and raises nothing, so test it with `( Goal -> ... ; ... )`.
**Run:** `eclipse.exe -f model.ecl -e main` (`eclipse.exe` must be on PATH, or call it by its full path)
**Expected:** `infeasible: no assignment exists`
**Time:** about 0.3 s wall, start-up included.
