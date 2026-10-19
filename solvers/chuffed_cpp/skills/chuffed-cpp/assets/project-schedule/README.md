# Project schedule with workers (scheduling, minimise)

**Problem:** 6 tasks with durations and worker demands, 4 precedences, at most 3 workers at any time; minimise the finishing time of the project.
**Shows:** start variables over a horizon from the data, `cumulative(start, duration, demand, capacity)`, precedences and end-by-makespan bounds with the offset form `int_rel(x, rel, y, c)` (x rel y + c), `branch(start, VAR_MIN_MIN, VAL_MIN)`, `optimize(makespan, OPT_MIN)`.
**Run:** `cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build && ./build/model`
**Expected:** `makespan 11 starts 0 0 3 2 7 10`
**Expected:** `Optimal makespan: 11`

The optimum 11 was checked by brute force over all start times. For one machine (no two tasks overlap) use `disjunctive(start, duration)`; see the [globals tour](../globals-tour/README.md).
