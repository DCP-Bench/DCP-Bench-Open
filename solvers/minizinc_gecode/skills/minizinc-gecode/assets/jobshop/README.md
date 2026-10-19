# Job shop, ragged jobs (minimise a makespan)

**Problem:** three jobs with 3, 3 and 2 tasks on three machines; each task needs one machine for a fixed duration, tasks of a job run in order, and no machine runs two tasks at once. Minimise the makespan.
**Shows:** ragged Python data flattened to 1-based arrays (`job`, `mach`, `dur`) with the job's row positions kept on the Python side; precedence with `where job[t] = job[t+1]`; `disjunctive` over a machine's tasks selected by a `where` comprehension; minimising a maximum (`s[t] + dur[t] <= makespan`, then `solve minimize makespan`).
**Run:** `python3 model.py`
**Expected:** `makespan = 11`
