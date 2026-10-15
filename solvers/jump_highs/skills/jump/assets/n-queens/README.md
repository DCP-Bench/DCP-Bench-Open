# N-queens (expressions in all-different)

**Problem:** Place 8 queens on an 8 by 8 board so that no two share a row, column or diagonal.
**Shows:** `MOI.AllDifferent` over affine expressions (q[i] + i, q[i] - i) whose variables have finite bounds, no auxiliary variables needed.
**Run:** `julia model.jl`
**Expected:** `Status: OPTIMAL`
**Expected:** `Valid: true`
