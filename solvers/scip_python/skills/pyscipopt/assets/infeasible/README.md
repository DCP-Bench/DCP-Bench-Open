# Staffing that cannot be met (infeasible)

**Problem:** Two shifts of at most 3 people each must cover a demand of 7.
**Shows:** the `"infeasible"` status, `getNSols()`, and why the status is checked before any value is read (`getVal` raises a `Warning` when there is no solution).
**Run:** `python model.py`
**Expected:** `Status: infeasible`
**Expected:** `Solutions found: 0`
**Expected:** `getVal refused: No solution available`
