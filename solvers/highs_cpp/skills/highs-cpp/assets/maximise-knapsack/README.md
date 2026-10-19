# 0/1 knapsack (maximise)

**Problem:** seven items with values and weights, capacity 9; maximise the total value plus a fixed bonus of 100.
**Shows:** binary columns, `changeColCost` with `changeObjectiveSense(kMaximize)`, `changeObjectiveOffset` (the objective includes the offset), `mip_rel_gap = 0` so `kOptimal` means proven.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -I"$HIGHS_PREFIX/include/highs" -L"$HIGHS_PREFIX/lib" -lhighs -lpthread && ./model`
**Expected:** `Maximum value: 115`
