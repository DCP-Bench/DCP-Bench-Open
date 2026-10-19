# Cumulative schedule (minimise makespan)

**Problem:** six tasks with durations and resource demands share a resource of capacity 3; two precedences; minimise the makespan.
**Shows:** `cumulative/4` from `lib(ic_edge_finder)` (`cumulative(Starts, Durations, Demands, Limit)`), precedences posted with `foreach` (a failure-driven loop would undo them), makespan as `max/1` of the end times, `bb_min/3`.
**Run:** `eclipse.exe -f model.ecl -e main` (`eclipse.exe` must be on PATH, or call it by its full path)
**Expected:** `Makespan: 9`
**Expected:** `f starts at 8`
**Time:** about 0.3 s wall, start-up included.
