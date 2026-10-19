# Job shop (scalable scheduling)

**Problem:** Fisher and Thompson ft06, six jobs on six machines, each job visits its machines in a fixed order; minimise the makespan (optimum 55).
**Shows:** a horizon from a greedy schedule and head/tail start domains; reified no-overlap over order-encoded starts, skipping selectors that come back `None`; the makespan as unit-weight soft clauses `[-makespan.ge(t)]` (cost = makespan - lower bound); decoding through a padded model; an independent schedule check.
**Run:** `python3 model.py`
**Expected:** `Makespan: 55`
**Expected:** `Schedule valid: True`
