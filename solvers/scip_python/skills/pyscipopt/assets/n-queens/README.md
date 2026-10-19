# N-queens (satisfy)

**Problem:** Place 8 queens on an 8x8 board so that no two share a row, column or diagonal.
**Shows:** one-hot binaries, linear constraints built with `quicksum`, no objective (satisfaction), `"optimal"` as the found-a-solution status, evaluating an expression in the solution with `getBestSol()[expr]`.
**Run:** `python model.py 8`
**Expected:** `Status: optimal`
**Expected:** `Queens: [`
