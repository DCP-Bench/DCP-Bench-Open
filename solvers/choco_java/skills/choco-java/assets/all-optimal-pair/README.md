# Cheapest pair (all optimal solutions)

**Problem:** choose exactly 2 of 4 items with costs 2, 1, 2, 5 at minimum total cost. Two different pairs tie.
**Shows:** Boolean choices with `sum`, a cost variable tied by `scalar`, minimising with `setObjective`, the proof check `getSearchState() == TERMINATED`, and enumerating every optimum on a fresh model with the cost fixed.
**Run:** `java Pair.java`
**Expected:** `Optimal cost: 3`
**Expected:** `Optimal solutions: 2`
**Expected:** `items [0, 1] cost 3`
