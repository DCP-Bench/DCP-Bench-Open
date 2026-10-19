# 0/1 knapsack (maximise)

**Problem:** choose among 5 items (weights 12, 7, 11, 8, 9; values 24, 13, 23, 15, 16) to maximise the value within capacity 26.
**Shows:** 0..1 decision variables, weighted `int_linear` over `vec<int>` / `vec<IntVar*>` copied from `std::vector`, an objective `IntVar` defined by `int_linear(..., IRT_EQ, profit)`, `optimize(profit, OPT_MAX)`, `print` called on each improving solution, `so.time_out`, and `engine.best_sol` with the time-out check.
**Run:** `cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build && ./build/model`
**Expected:** `profit 51 take 0 1 1 1 0`
**Expected:** `Optimal profit: 51`

An optimisation search keeps improving until it proves no better solution exists (it ignores `so.nof_solutions`); it ends with `engine.status` `RES_LUN`, or `RES_UNK` on a time out, when the last solution is only the best found.
