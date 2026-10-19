# Minimum makespan on three machines (minimise, all optimal solutions)

**Problem:** assign 6 jobs with durations 3, 5, 2, 7, 4, 6 to 3 machines so that the largest total load is as small as possible; then list every assignment with that makespan.
**Shows:** a variable per job holding its machine, `isEq` and `mul` to turn an assignment into loads, `max` over the loads, `minimize` with a proof check, and enumerating every optimum: fix the objective, then forbid each assignment found with a no-good.
**Run:** `java MinMakespan.java`
**Expected:** `Optimal makespan: 9`
**Expected:** `Optimal assignments: 6`
