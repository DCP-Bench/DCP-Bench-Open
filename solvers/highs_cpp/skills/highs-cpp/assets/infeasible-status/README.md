# Infeasible model (status check)

**Problem:** an integer x in 0..5 with 2x = 7.
**Shows:** that `run()` returns `kOk` for an infeasible model and the verdict is `getModelStatus()`; `modelStatusToString` gives the name.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -I"$HIGHS_PREFIX/include/highs" -L"$HIGHS_PREFIX/lib" -lhighs -lpthread && ./model`
**Expected:** `Status: Infeasible`
