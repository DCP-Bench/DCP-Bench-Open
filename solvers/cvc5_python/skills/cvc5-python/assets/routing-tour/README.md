# Closed tour (routing, minimise)

**Problem:** shortest tour that visits every city once and returns to city 0. Distance matrix in `data.json` under `"dist"`.
**Shows:** successor variables with `Distinct` (a permutation), subtour elimination with position variables and `Implies`, leg cost by enumeration, minimisation by tightening.
**Run:** `python model.py` (or `python model.py other.json`)
**Expected:** `Optimal tour length: 31`
