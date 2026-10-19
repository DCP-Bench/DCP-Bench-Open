# Assignment with one-hot binaries (satisfy)

**Problem:** 4 jobs on 3 machines; one machine per job, at most two jobs per machine, jobs 0 and 1 apart.
**Shows:** binary columns, one-hot rows, `addRow` with `kHighsInf` bounds, status check after `run()`, reading `getSolution().col_value`.
**Run:** `g++ -std=c++17 -O2 model.cpp -o model -I"$HIGHS_PREFIX/include/highs" -L"$HIGHS_PREFIX/lib" -lhighs -lpthread && ./model`
**Expected:** `status: Optimal`
**Expected:** `job 0 -> machine`
