# Job-shop ft06 (minimise makespan)

**Problem:** Six jobs, six machines, each job's tasks in order, one task at a time per machine. Minimise the makespan of Fisher and Thompson's ft06.
**Shows:** start-time variables over a horizon equal to the sum of durations, precedence within a job, pairwise no-overlap on each machine as two reified orders with one required, and minimisation with `toOptimum`.
**Run:** `python3 model.py`
**Expected:** `status: SAT`
**Expected:** `makespan: 55`
