# Job shop with makespan (no overlap per machine, precedence within jobs)

**Problem:** Three jobs on three machines; each job visits its machines in its own order. Minimise the makespan (the finish time of the last operation).
**Shows:** one start variable per operation, precedence rows along each job, one no-overlap binary per pair of operations on the same machine (big-M from the total duration), a makespan variable bounded below by each job's last operation.
**Run:** `python3 model.py`
**Expected:** `Status: Optimal`
**Expected:** `Makespan: 11`
