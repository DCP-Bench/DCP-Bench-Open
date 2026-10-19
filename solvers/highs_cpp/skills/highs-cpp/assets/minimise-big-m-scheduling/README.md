# Two jobs on one machine (minimise, big-M disjunction)

**Problem:** jobs of length 3 and 4 on one machine, no overlap, all released at 0; minimise the makespan.
**Shows:** a disjunction linearised with one binary and a big-M from the total work, a continuous objective column, `changeColCost` with `kMinimize`, reading the start times.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -I"$HIGHS_PREFIX/include/highs" -L"$HIGHS_PREFIX/lib" -lhighs -lpthread && ./model`
**Expected:** `Makespan: 7`
