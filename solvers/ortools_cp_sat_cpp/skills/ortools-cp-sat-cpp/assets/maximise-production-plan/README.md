# Production plan (maximise)

**Problem:** integer quantities of chairs and tables, profit 40 and 50 per unit, under two capacity limits.
**Shows:** `NewIntVar` with bounds, `AddLessOrEqual` with linear expressions, `Maximize`, the proven-optimal check, reading integer values from the solution.
**Run:** `cmake -S . -B build && cmake --build build && ./build/model`
**Expected:** `Status: OPTIMAL`
**Expected:** `Maximum profit: 410`
**Expected:** `chairs = 4`

Needs `CMAKE_PREFIX_PATH` pointing at the OR-Tools folder; see the skill's Install section.
