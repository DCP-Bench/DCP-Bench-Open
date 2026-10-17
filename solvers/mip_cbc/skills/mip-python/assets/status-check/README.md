# Status check (infeasible, unbounded, proven optimum)

**Problem:** Three small models: one with no solution, one with an unbounded objective, one solved with exact gap settings.
**Shows:** reading the status of `optimize` (INFEASIBLE, UNBOUNDED, OPTIMAL), values are `None` without a solution, `max_mip_gap = 0` so OPTIMAL means proven.
**Run:** `python model.py`
**Expected:** `infeasible model: INFEASIBLE | p.x = None`
**Expected:** `unbounded model: UNBOUNDED | t.x = None`
**Expected:** `knapsack: OPTIMAL | value 12 | gap 0.0`
