# Four tasks on a shared resource (scheduling)

**Problem:** start four tasks with durations 3, 2, 4, 2 and resource demands 1, 2, 1, 2 on a resource of capacity 2, where task 1 precedes task 3 and task 2 precedes task 4, minimising the makespan.
**Shows:** `cumulative/4` over start times, precedence as linear inequalities, a horizon from the data, `$min` over the makespan variable.
**Run:** `picat model.pi`
**Expected:** `Makespan: 11`
