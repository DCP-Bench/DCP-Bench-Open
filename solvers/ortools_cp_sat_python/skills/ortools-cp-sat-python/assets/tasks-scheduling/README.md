# Tasks with a shared resource (scheduling)

**Problem:** five tasks with durations, resource demands (capacity 2) and four precedences; minimise the finish time of the last task.
**Shows:** interval variables, `add_cumulative`, precedence constraints on start and end, a makespan defined with `add_max_equality`, `minimize`.
**Run:** `python3 model.py`
**Expected:** `OPTIMAL`
**Expected:** `Makespan: 11`
