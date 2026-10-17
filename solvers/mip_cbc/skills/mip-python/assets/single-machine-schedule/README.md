# Single-machine schedule with release times (minimise)

**Problem:** Three jobs with durations 3, 2, 4 and release times 0, 2, 1 share one machine. Minimise the makespan.
**Shows:** integer start times with bounds from the data, a big-M no-overlap constraint for each pair of jobs (M computed from the data), a makespan variable as the objective.
**Run:** `python model.py`
**Expected:** `Makespan: 9`
**Expected:** `job 2: start 3, finish 7`
