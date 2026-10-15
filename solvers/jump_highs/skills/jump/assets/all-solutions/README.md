# All solutions

**Problem:** Every integer pair (x, y) in 0..4 with x + 2y = 6.
**Shows:** enumeration by repeated solves and no-good cuts over bounded integer variables, the big-M disjunction that excludes one assignment, the status that ends the loop.
**Run:** `julia model.jl`
**Expected:** `Solutions: 3`
**Expected:** `x = 2, y = 2`
**Expected:** `Status after the last solve: INFEASIBLE`
