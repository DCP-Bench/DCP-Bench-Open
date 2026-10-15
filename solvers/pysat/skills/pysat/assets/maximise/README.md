# Worker assignment (maximise)

**Problem:** three workers, three jobs, one job each, maximum total profit.
**Shows:** exact-one and at-most-one constraints with `CardEnc`, maximisation as soft clauses `[x]` weighted by profit, reading the optimum back from the model, a brute-force cross-check.
**Run:** `python3 model.py`
**Expected:** `Maximum profit: 24`
**Expected:** `Matches brute force: True`
**Expected:** `Cost agrees: True`
