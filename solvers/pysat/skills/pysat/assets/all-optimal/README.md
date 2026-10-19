# Set covers (all optimal solutions)

**Problem:** cover six elements with named sets of given costs; list every cover of minimum cost.
**Shows:** enumerating optimal solutions with RC2: solve, keep models while their cost equals the optimum, block each one with `add_clause`, stop at the first worse cost.
**Run:** `python3 model.py`
**Expected:** `Optimum: 3`
**Expected:** `Number of optimal covers: 2`
**Expected:** `Matches brute force: True`
