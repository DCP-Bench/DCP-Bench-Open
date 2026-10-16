# Single machine with precedences and release times (scheduling)

**Problem:** four tasks with durations 3, 2, 4, 2 on one machine; task 0 must end before task 2 starts, task 1 before task 3; task 3 cannot start before time 4. Minimise the makespan.
**Shows:** interval variables that must run (`makeIntervalVar(cp, false, length)`), `noOverlap`, `endBeforeStart`, `startAfter`, `makespan`, branching on `start` views with `firstFailBinary`, and the proof check on `optimize`.
**Run:** `java SingleMachine.java`
**Expected:** `Makespan: 11`
**Expected:** `Proven optimal: true`
