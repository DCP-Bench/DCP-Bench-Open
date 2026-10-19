# Magic square of order 3 (satisfy)

**Problem:** Fill a 3x3 grid with the numbers 1 to 9, each once, so every row, column and both diagonals sum to 15.
**Shows:** integer variables with explicit bounds, `z3.Distinct`, `z3.Sum` over lines, `Solver.check()` against `z3.sat`, reading values with `model.eval(..., model_completion=True)`.
**Run:** `python3 model.py`
**Expected:** `magic constant: 15`
**Expected:** `all lines sum to 15: True`
