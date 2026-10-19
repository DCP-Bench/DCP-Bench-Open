# Pigeonhole (infeasible)

**Problem:** put 5 pigeons into 4 holes with at most one pigeon per hole.
**Shows:** how Chuffed reports infeasibility. Here `all_different` already fails at the root: Chuffed prints `=====UNSATISFIABLE=====` and `% Top level failure!` and calls `exit(0)`, so `engine.solve` never returns and `engine.status` is never set. A `std::atexit` handler with a flag set after `engine.solve` tells this apart. An infeasibility proven later by search returns normally with `engine.solutions == 0` (see the [queens](../queens/README.md) example with n = 3).
**Run:** `cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build && ./build/model`
**Expected:** `=====UNSATISFIABLE=====`
**Expected:** `Infeasible: failed at the root, before search`

The process exits with code 0 in both cases; do not read a zero exit code as "solved".
