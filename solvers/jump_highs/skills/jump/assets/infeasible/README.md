# Infeasible

**Problem:** Integers x, y in 0..2 with x + y >= 5.
**Shows:** how a proven infeasible model reports itself: the termination status, and `has_values` false so no value is read.
**Run:** `julia model.jl`
**Expected:** `Status: INFEASIBLE`
**Expected:** `Has a solution: false`
