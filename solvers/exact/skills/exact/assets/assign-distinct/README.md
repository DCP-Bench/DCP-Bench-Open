# Assign distinct desks (satisfy)

**Problem:** Four people, four desks, each person one desk, every desk taken once, Ann not at desk 0.
**Shows:** one-hot indicators built from `addVariable` and `addConstraint`; a `runFull(optimize=False)` satisfaction call; reading values with `getLastSolutionFor`.
**Run:** `python3 model.py`
**Expected:** `status: SAT`
**Expected:** `all desks different: True`
**Expected:** `Ann not at desk 0: True`
