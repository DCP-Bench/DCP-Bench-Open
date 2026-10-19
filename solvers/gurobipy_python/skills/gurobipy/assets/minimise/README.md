# Worker assignment (minimise)

**Problem:** Assign three workers to three jobs, one each, at minimum total cost.
**Shows:** binary matrix of decisions, `addConstrs` over a generator with `x.sum`, `GRB.MINIMIZE`, reading the chosen pairs.
**Run:** `python3 model.py`
**Expected:** `Total cost: 9`
