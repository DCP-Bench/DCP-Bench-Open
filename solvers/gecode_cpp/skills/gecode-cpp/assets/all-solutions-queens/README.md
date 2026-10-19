# n-queens, every solution (all solutions)

**Problem:** list every placement of 8 queens on an 8 x 8 board with no two attacking each other.
**Shows:** `distinct` with offsets for the diagonals, a `DFS` loop on `next()` until `nullptr`, `stopped()` to tell exhaustion from a limit, a size from `argv`.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -lgecodesearch -lgecodeminimodel -lgecodeset -lgecodefloat -lgecodeint -lgecodekernel -lgecodesupport && ./model 8`
**Expected:** `First: 0 4 7 5 2 6 1 3`
**Expected:** `Solutions: 92 (all)`

Each solution is one assignment of the branched array `q`, so none repeats. 92 is the known count for 8 queens. Adapted from Gecode's `examples/queens.cpp`.
