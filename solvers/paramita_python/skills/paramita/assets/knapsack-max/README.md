# Knapsack (maximise)

**Problem:** 0/1 knapsack with 3 items, capacity 7 (optimum 90, items 1 and 2).
**Shows:** a weighted PB constraint, a linear objective, `EvalMaxSAT2022` with `add_to_weighted_container` (which maximises), the constant part plus `benefit()`, the proven-optimal status check.
**Run:** `python3 model.py`
**Expected:** `Optimum: 90`
