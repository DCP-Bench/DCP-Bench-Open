# Graph colouring (minimise)

**Problem:** Colour the 10 nodes of the Petersen graph so that adjacent nodes differ, using as few colours as possible.
**Shows:** one-hot node-by-colour indicators with an exactly-one row per node, used-colour variables that the objective sums, edge constraints as `<= 1` on pairs of indicators, and reading `toOptimum` only when the state is `SAT`.
**Run:** `python3 model.py`
**Expected:** `colours used: 3`
**Expected:** `proper colouring: True`
