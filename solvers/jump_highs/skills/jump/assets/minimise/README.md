# Minimise (set cover)

**Problem:** Pick sets with the least total cost so that every element 1..5 is covered.
**Shows:** binary variables per set, covering constraints written as sums over a membership test, `@objective(model, Min, ...)`, reading which binaries are 1.
**Run:** `julia model.jl`
**Expected:** `Status: OPTIMAL`
**Expected:** `Minimum cost: 6`
