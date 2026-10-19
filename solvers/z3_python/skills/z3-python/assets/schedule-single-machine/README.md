# One machine with release times and precedences (scheduling)

**Problem:** Four tasks with durations and release times share one machine; cut before paint, weld before dry. Minimise the makespan.
**Shows:** scheduling by pairwise disjunction (Z3 has no `NoOverlap` or `Cumulative`), precedence and release constraints, `Optimize.minimize`, reading start times.
**Run:** `python3 model.py`
**Expected:** `Minimum makespan: 11`
**Expected:** `proven optimal: True`
