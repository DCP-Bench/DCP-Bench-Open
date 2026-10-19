# Maximum-weight independent set (maximise)

**Problem:** Pick vertices of a 6-cycle, with weights 5, 3, 8, 2, 7, 4, so that no two adjacent vertices are picked and the total weight is largest.
**Shows:** maximise through soft clauses on the literal itself (pay for what is left out), converting `r.cost` back to the objective.
**Run:** `python3 model.py`
**Expected:** `best weight 20`
