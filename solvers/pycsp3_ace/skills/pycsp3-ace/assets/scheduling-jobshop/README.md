# Job shop (scheduling)

**Problem:** three jobs; each job's tasks run in order, a machine runs one task at a time; minimise the makespan. The machines are taken from the task list, so the model needs no machine count (a six-machine instance also solves to OPTIMUM).
**Shows:** start-time variables in one flat `VarArray`, precedences, `NoOverlap(origins=..., lengths=...)` per machine, `Maximum` of expressions for the makespan, `minimize`.
**Run:** `python model.py`
**Expected:** `Makespan: 11`
