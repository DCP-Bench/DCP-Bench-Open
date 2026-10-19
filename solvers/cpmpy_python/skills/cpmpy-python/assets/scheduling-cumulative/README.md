# Project schedule (scheduling, minimise makespan)

**Problem:** six tasks with durations, resource demands and precedences on a resource of capacity 2; minimise the finish time of the last task. Data in `tasks.json`.
**Shows:** `Cumulative` with explicit `end` variables, precedences as linear constraints, reading data from a JSON file given on the command line, an independent check of the result.
**Run:** `python3 model.py tasks.json`
**Expected:** `Makespan: 13`
**Expected:** `Proven optimal: True`
