# Pigeonhole (infeasible)

**Problem:** put 4 pigeons into 3 holes, one pigeon per hole.
**Shows:** the two ways infeasibility shows up: the root space fails during propagation (`status() == SS_FAILED`, with `distinct` at `IPL_DOM`), or `DFS` returns `nullptr` without `stopped()` (default level, after a search). Also `engine.statistics()`.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -lgecodesearch -lgecodeminimodel -lgecodeset -lgecodefloat -lgecodeint -lgecodekernel -lgecodesupport && ./model`
**Expected:** `IPL_DOM: no placement, root propagation failed`
**Expected:** `IPL_DEF: no placement, search exhausted after`
