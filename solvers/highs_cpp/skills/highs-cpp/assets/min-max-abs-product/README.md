# Absolute value, maximum, indicators and a product (minimise)

**Problem:** x + y = 7 over 0..7; minimise |x - y| + max(x, y) + 10 * p, where p is the product of the indicators b1 = (x >= 4) and b2 = (y >= 4).
**Shows:** absolute value and max by two-sided rows, indicator linearisation from both sides, a product of binaries, the objective's constant zero and integer rounding of the result.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -I"$HIGHS_PREFIX/include/highs" -L"$HIGHS_PREFIX/lib" -lhighs -lpthread && ./model`
**Expected:** `Objective: 5`
**Expected:** `product p = 0`
