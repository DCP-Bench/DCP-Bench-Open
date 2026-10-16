# Tasks on one machine (no overlap)

**Problem:** Three tasks of durations 2, 3 and 1 share one machine, so they cannot overlap; task 0 must finish before task 2 starts. Minimise the makespan.
**Shows:** a no-overlap (disjunctive) machine as `cumulative` with unit heights and capacity 1, IntVar heights.
**Run:** `python3 model.py`
**Expected:** `Makespan: 6`
