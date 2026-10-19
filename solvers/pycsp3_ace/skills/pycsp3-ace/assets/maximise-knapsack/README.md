# Knapsack (maximise)

**Problem:** 0/1 knapsack with 4 items and capacity 8.
**Shows:** Boolean `VarArray` (`dom={0, 1}`), a weighted `Sum` constraint, `maximize`, `OPTIMUM` versus `SAT` (unproven), `bound()` for the objective value, not shadowing pycsp3's `values`.
**Run:** `python model.py`
**Expected:** `Objective: 29`
**Expected:** `Take: [1, 0, 1, 1]`
