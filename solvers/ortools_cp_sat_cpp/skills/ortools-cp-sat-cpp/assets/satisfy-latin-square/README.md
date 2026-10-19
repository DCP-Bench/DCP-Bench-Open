# Latin square completion (satisfy)

**Problem:** complete a 4x4 Latin square (every row and column holds 1..4 once) from 6 given cells.
**Shows:** integer variables with a domain, `AddAllDifferent` per row and column, clues as equalities, reading a solution, the status check before reading values.
**Run:** `cmake -S . -B build && cmake --build build && ./build/model`
**Expected:** `Status: OPTIMAL`
**Expected:** `1 2 3 4`

Needs `CMAKE_PREFIX_PATH` pointing at the OR-Tools folder; see the skill's Install section. Build with CMake: `CMakeLists.txt` links `ortools::ortools`.
