# Three tasks on one machine (scheduling)

**Problem:** tasks of length 3, 2 and 2 on one machine; task 0 must finish before task 2 starts; minimise the makespan.
**Shows:** start-time variables, `cumulative` with capacity 1 as a no-overlap constraint, precedence and makespan bounds, `minimise`.
**Run:** `NO_CHECKERS=true cargo run --quiet`
**Expected:** `makespan: 7`
**Expected:** `start times: [`
