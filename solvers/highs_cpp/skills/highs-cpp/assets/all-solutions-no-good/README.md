# All solutions with no-goods (satisfy, enumerate)

**Problem:** the solutions of x + y = 2 with 0 <= x, y <= 2.
**Shows:** a no-good loop: solve, record, forbid the assignment over the integer columns with big-M indicators, solve again until infeasible. The final status is `Infeasible`.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -I"$HIGHS_PREFIX/include/highs" -L"$HIGHS_PREFIX/lib" -lhighs -lpthread && ./model`
**Expected:** `Solutions: 3 (last status: Infeasible)`
**Expected:** `x = 1, y = 1`
