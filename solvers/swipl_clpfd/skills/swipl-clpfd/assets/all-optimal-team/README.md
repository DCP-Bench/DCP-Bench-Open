# Cheapest team (all optimal solutions)

**Problem:** choose 3 of 5 people with costs 3, 1, 4, 1, 3 for the lowest total cost; list every cheapest team.
**Shows:** `labeling([min(Expr)], Vars)` for the optimum, fixing `Expr #= Optimum` and re-enumerating for all optimal solutions, `sum/3`.
**Run:** `swipl model.pl`
**Expected:** `Optimal cost: 5`
**Expected:** `Optimal teams: 2`
