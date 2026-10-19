# Worker-task assignment (all optimal solutions)

**Problem:** Assign 3 workers to 3 tasks, one each, at minimum total cost (costs from a 2-D list); list every cheapest assignment.
**Shows:** two index types sized from a 2-D list; `?=1` (exactly one); a two-variable `sum{{ }}`; `Theory.optimize(term, minimize=True)` followed by `Theory.expand(max=0)`, which enumerates only the optimal models; reading `does(w, t)` by its key `"does(0, 1)"`.
**Run:** `python model.py`
**Expected:** `Optimal assignments: 2`
**Expected:** `total 5`
