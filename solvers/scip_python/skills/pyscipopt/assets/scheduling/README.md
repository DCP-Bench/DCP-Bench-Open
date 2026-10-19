# Crew scheduling (scheduling, minimise)

**Problem:** Five tasks with durations and worker demands share 3 workers; task 3 follows task 0. Minimise the makespan (9: tasks 0, 2 and 3 each need 2 of the 3 workers, so they run one after another).
**Shows:** `addConsCumulative` over integer start variables with constant durations and demands, a precedence, a makespan variable bounded below by every end.
**Run:** `python model.py`
**Expected:** `Status: optimal`
**Expected:** `Makespan: 9`
