# Job shop (minimise makespan)

**Problem:** 3 jobs, each visits 3 machines in a fixed order; a machine runs one operation at a time. Minimise the time the last operation ends. Data in `data.json`, format `{"jobs": [[[machine, duration], ...], ...]}`.
**Shows:** start-time variables, precedence, no-overlap as a pairwise `Or` per pair of operations on a machine, minimisation by tightening until `unsat`.
**Run:** `python model.py` (or `python model.py other.json`)
**Expected:** `Optimal makespan: 11`
