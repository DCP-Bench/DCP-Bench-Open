# Weighted vertex cover (minimise)

**Problem:** cover the edges of a 6-vertex graph with vertices of minimum total cost.
**Shows:** hard clauses for constraints, one soft clause `[-x]` per variable with weight equal to its cost, `RC2Stratified.compute()` and `cost`, a brute-force cross-check.
**Run:** `python3 model.py`
**Expected:** `Minimum cost: 7`
**Expected:** `Matches brute force: True`
