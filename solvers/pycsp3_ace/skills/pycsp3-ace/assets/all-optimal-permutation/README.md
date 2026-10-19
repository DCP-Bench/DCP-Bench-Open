# All optimal solutions

**Problem:** three distinct values in 0..4 with x0 < x1, maximising x0 + x1 + x2; list every assignment that reaches the optimum.
**Shows:** the two-step recipe: `maximize` and `bound()` after an `OPTIMUM` status, then `clear()`, rebuild through a function with an explicit `id=`, post `score == best` and enumerate with `sols=ALL`.
**Run:** `python model.py`
**Expected:** `Optimum: 9`
**Expected:** `Optimal solutions: 3`
