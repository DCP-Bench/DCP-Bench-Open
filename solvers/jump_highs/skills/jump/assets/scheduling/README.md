# Scheduling (two-machine job shop)

**Problem:** Job 1 runs machine 1 (3 units) then machine 2 (2 units); job 2 runs machine 2 (4), machine 1 (2), machine 2 (1). Minimise the makespan.
**Shows:** start-time vectors sized per job (ragged input), precedence chains, disjunctive no-overlap with a big-M and a binary order per pair, minimise a makespan variable.
**Run:** `julia model.jl`
**Expected:** `Status: OPTIMAL`
**Expected:** `Makespan: 7`
