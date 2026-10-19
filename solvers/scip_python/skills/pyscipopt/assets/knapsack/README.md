# Knapsack (maximise)

**Problem:** 0/1 knapsack with 4 items (weights 3, 4, 2, 5; values 40, 50, 30, 60) and capacity 7.
**Shows:** binary variables, a linear capacity constraint, `setObjective(..., "maximize")`, the proven-optimal status check, rounding values read with `getVal`.
**Run:** `python model.py`
**Expected:** `Status: optimal`
**Expected:** `Objective: 90`
