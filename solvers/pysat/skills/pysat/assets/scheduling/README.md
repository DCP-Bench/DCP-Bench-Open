# Single-machine schedule (scheduling)

**Problem:** four jobs on one machine with durations, release times and one precedence; minimise the makespan.
**Shows:** `Integer` start times with domains from release times, reified `add_linear(..., reified=True)` for no-overlap disjunctions, a makespan as soft clauses `[-x == t]` weighted `t`, decoding through a dense model, a brute-force cross-check.
**Run:** `python3 model.py`
**Expected:** `Makespan: 11`
**Expected:** `Optimal: True`
**Expected:** `Matches brute force: True`
