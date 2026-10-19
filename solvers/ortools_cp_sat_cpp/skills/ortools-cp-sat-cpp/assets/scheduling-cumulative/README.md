# Resource-constrained project schedule (scheduling)

**Problem:** five tasks with durations, resource demands, precedences and a shared resource of capacity 3; minimise the makespan.
**Shows:** `NewFixedSizeIntervalVar`, `AddCumulative` with `AddDemand`, precedence as `AddGreaterOrEqual`, a makespan variable with `Minimize`.
**Run:** `cmake -S . -B build && cmake --build build && ./build/model`
**Expected:** `Status: OPTIMAL`
**Expected:** `Makespan: 10`

Needs `CMAKE_PREFIX_PATH` pointing at the OR-Tools folder; see the skill's Install section. For a single unary machine use `AddNoOverlap` over the same intervals instead of `AddCumulative`.
