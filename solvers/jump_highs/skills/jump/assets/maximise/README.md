# Maximise (integer production plan)

**Problem:** Integer units a, b >= 0 of two products with 6a + 4b <= 24 and a + 2b <= 6, maximising 5a + 4b.
**Shows:** integer variables with a lower bound only, `@objective(model, Max, ...)`, the status check for a proven optimum, rounding a value to an integer.
**Run:** `julia model.jl`
**Expected:** `Status: OPTIMAL`
**Expected:** `Profit: 20`
