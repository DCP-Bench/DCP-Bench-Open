# Job shop with no-overlap machines (scheduling)

**Problem:** three jobs, each a fixed sequence of three operations on three machines; a machine runs one operation at a time; minimise the makespan.
**Shows:** `NewFixedSizeIntervalVar` for each operation, `AddNoOverlap` on a `std::vector<IntervalVar>` with one call per machine, precedence inside a job as `AddGreaterOrEqual`, and the makespan as a `Minimize` target.
**Run:** `cmake -S . -B build && cmake --build build && ./build/model`
**Expected:** `Status: OPTIMAL`
**Expected:** `Makespan: 11`

Needs `CMAKE_PREFIX_PATH` pointing at the OR-Tools folder; see the skill's Install section. The optimum was checked by enumerating every operation order on each machine in Python.
