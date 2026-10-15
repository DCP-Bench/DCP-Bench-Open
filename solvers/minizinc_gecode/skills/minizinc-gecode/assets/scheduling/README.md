# Two workers, five tasks (scheduling, minimise)

**Problem:** start times for five tasks on two workers with precedences; minimise the makespan.
**Shows:** `cumulative` for a shared resource with demands, precedence constraints as `<=` on start times, `solve minimize` on a makespan variable.
**Run:** `minizinc --solver gecode model.mzn`
**Expected:** `makespan = 9`
