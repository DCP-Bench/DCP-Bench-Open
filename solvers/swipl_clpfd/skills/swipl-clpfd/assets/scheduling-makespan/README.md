# Two machines (scheduling)

**Problem:** four tasks with durations 3, 2, 2, 4; t1 before t3, t2 before t4; two machines; minimise the makespan.
**Shows:** `cumulative/2` with `task/5` and `limit/1`, precedences as inequalities between start and end variables, `labeling([min(Expr)], Vars)`.
**Run:** `swipl model.pl`
**Expected:** `Makespan: 6`
