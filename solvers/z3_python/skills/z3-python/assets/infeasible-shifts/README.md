# Impossible roster (infeasible)

**Problem:** Three people, each 0 to 3 hours, must total exactly 10 hours.
**Shows:** that an infeasible model is reported by the status `unsat` from `check()`, not by an exception; the `unknown` branch with `reason_unknown()`.
**Run:** `python3 model.py`
**Expected:** `status: unsat`
