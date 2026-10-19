# Cheapest committee, every optimal choice (all optimal solutions)

**Problem:** choose 3 of 6 candidates at minimum total cost, with at least one from group A (0..2) and one from group B (3..5).
**Shows:** the all-optimal pattern: `BAB` on an `IntMinimizeSpace` proves the optimum, then a fresh space with `total == optimum` is enumerated with `DFS`. Also `BoolVarArray`, `linear` over Booleans, `slice`.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -lgecodesearch -lgecodeminimodel -lgecodeset -lgecodefloat -lgecodeint -lgecodekernel -lgecodesupport && ./model`
**Expected:** `Optimal cost: 5`
**Expected:** `Optimal choices: 3`

The second phase uses `DFS`, not `BAB`: `BAB` keeps posting "strictly better than the last solution", so it would never return a second solution of equal cost. The three optimal committees were checked by hand.
