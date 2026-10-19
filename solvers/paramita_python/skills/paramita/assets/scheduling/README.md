# One-machine scheduling with deadlines (satisfy)

**Problem:** three jobs (durations 2, 3, 2; deadlines 4, 7, 5) on one machine, no overlap.
**Shows:** one-hot start times, a reified "running in slot t" Boolean per job and slot, at-most-one per slot as the no-overlap constraint, reading start times back from the model.
**Run:** `python3 model.py`
**Expected:** `job 0 starts at`
**Expected:** `job 2 starts at`
