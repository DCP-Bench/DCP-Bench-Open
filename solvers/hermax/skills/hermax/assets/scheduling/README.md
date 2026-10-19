# Shared-resource scheduling (scheduling)

**Problem:** Four tasks with durations 3, 2, 4, 2 and resource demands 1, 1, 2, 1 share a resource of capacity 2; task A must finish before C starts and B before D. Minimise the makespan.
**Shows:** `int_vector` start times, `cumulative` (which adds its own constraint, so it is not wrapped in `m &=`), precedences as linear inequalities, a makespan integer as the objective.
**Run:** `python3 model.py`
**Expected:** `Makespan: 8`
