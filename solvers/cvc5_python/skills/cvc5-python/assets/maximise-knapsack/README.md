# 0/1 knapsack (maximise)

**Problem:** choose items with values and weights, total weight at most the capacity, maximise total value. Data in `data.json` (8 items, capacity 26).
**Shows:** Boolean decision variables, `Sum(If(...))` for weighted sums, optimisation by tightening (`value > best`) until `unsat` proves the optimum, JSON data file with the path as argument.
**Run:** `python model.py` (or `python model.py other.json`)
**Expected:** `Optimal value: 52`
