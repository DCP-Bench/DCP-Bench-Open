# Staffing that cannot be met (infeasible)

**Problem:** Two shifts of at most 3 people each must cover a demand of 7.
**Shows:** the `INFEASIBLE` status, `computeIIS` to find the conflicting constraints, why a status must be checked before reading values.
**Run:** `python3 model.py`
**Expected:** `Status: INFEASIBLE`
**Expected:** `Conflicting constraints: ['demand']`
