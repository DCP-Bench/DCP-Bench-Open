# Satisfy

**Problem:** Find a permutation x of 1..4 with x[1] < x[2] and x[3] + x[4] = 5.
**Shows:** integer variables with bounds, `MOI.AllDifferent`, linear constraints, a model without an objective, reading values.
**Run:** `julia model.jl`
**Expected:** `Status: OPTIMAL`
**Expected:** `Valid: true`
