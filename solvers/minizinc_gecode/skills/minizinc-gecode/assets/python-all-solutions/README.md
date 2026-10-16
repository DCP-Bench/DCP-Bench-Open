# Duplicates from Python all_solutions (satisfy)

**Problem:** x in 1..3 with x <= 2, and a helper variable `aux` in 0..1 that nothing constrains.
**Shows:** `instance.solve(all_solutions=True)` returns one object per solution of every variable, so the free helper doubles the count; `result.solution` is a list (empty when there are none); keeping the distinct output values gives the CLI answer.
**Run:** `python3 model.py`
**Expected:** `solutions counted by Python: 4`
**Expected:** `distinct values of x: [1, 2]`
