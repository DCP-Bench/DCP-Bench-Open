# Subsets summing to 9 (all solutions)

**Problem:** Choose a subset of the weights 2, 3, 4, 5, 6 whose sum is exactly 9.
**Shows:** enumeration by repeated `check()` with a blocking clause (`z3.Or` of inequalities) over the Boolean decision variables only; an auxiliary `Int` that is left out of the blocking clause.
**Run:** `python3 model.py`
**Expected:** `Solutions: 3`
**Expected:** `solution 1: [2, 3, 4]`
