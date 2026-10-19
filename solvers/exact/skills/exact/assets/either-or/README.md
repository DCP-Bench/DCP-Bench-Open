# Either-or conditions (reification)

**Problem:** A value x in 0..10 must be at most 3 or at least 8, and at least 5. Minimise x.
**Shows:** `addReification` with the head variable as a switch, a disjunction over two switches, and a minimisation.
**Run:** `python3 model.py`
**Expected:** `x = 8 minimum: 8`
