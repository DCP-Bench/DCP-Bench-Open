# Production plan (maximise)

**Problem:** Integer numbers of chairs and tables, with labour and wood limits, maximising profit 5 per chair and 4 per table.
**Shows:** `setObjective(..., minimize=False)`, `toOptimum` returning `SAT` only when proven, and undoing the sign of a maximisation.
**Run:** `python3 model.py`
**Expected:** `Optimal profit: 20`
**Expected:** `chairs=4 tables=0`
