# Job shop (scheduling, minimise makespan)

**Problem:** three jobs, each a fixed sequence of machine operations with durations; each machine processes one operation at a time; minimise the finish time of the last operation.
**Shows:** `NoOverlap` once per machine (the disjunctive pattern), job order as linear precedences between a job's `end` and next `start`, `zip(*tasks)` to unpack the per-machine lists, `minimize` on a makespan variable.
**Run:** `python3 model.py`
**Expected:** `Makespan: 11`
**Expected:** `Proven optimal: True`
