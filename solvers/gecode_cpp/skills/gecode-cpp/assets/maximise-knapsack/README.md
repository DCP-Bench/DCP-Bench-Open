# 0/1 knapsack (maximise)

**Problem:** six items with values and weights, capacity 47; maximise the total value.
**Shows:** `IntMaximizeSpace` with `cost()`, `linear` with weights over Booleans, `expr(*this, sum(IntArgs, x))`, `Search::Options` with `threads` and `Stop::time`, whether a stop cut the search short, read with `engine.stopped()`.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -lgecodesearch -lgecodeminimodel -lgecodeset -lgecodefloat -lgecodeint -lgecodekernel -lgecodesupport && ./model`
**Expected:** `Maximum value: 41`

The optimum 41 was checked by enumerating all 64 subsets in Python (two subsets reach it; Gecode reports the last one BAB found).
