# All optimal solutions

**Problem:** Choose binary items (values 5,5,5,1; weights 2,2,2,3) with total weight at most 4 to maximise value.
**Shows:** binary variables, maximise, pinning the optimum as a constraint, switching to feasibility sense, enumeration over binary variables.
**Run:** `julia model.jl`
**Expected:** `Optimal value: 10`
**Expected:** `Optimal selections: 3`
**Expected:** `items [2, 3]`
