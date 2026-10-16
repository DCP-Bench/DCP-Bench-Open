# All different with binaries (minimise)

**Problem:** x0..x3 take values 1..4, all different, x0 > x1; minimise x0 + 2 x1 + 3 x2 + 4 x3.
**Shows:** `alldifferent` as one-hot binaries (`x_i = sum (v) y[i][v]`, at most one variable per value), a strict order between integers written as `>= 1`, a weighted objective.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -I"$HIGHS_PREFIX/include/highs" -L"$HIGHS_PREFIX/lib" -lhighs -lpthread && ./model`
**Expected:** `Objective: 20`
