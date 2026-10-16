# Job shop (minimise the makespan, no-overlap on machines)

**Problem:** three jobs of three tasks each, each task on a given machine with a duration; a job's tasks run in the listed order, a machine runs one task at a time; finish all jobs as early as possible.
**Shows:** a no-overlap constraint written pairwise as an either-or (`\/` between the two orders) over a flat task list, precedences as an implication on a parameter condition (`jobof[a] = jobof[a+1]`), a horizon from `letting horizon = sum(dur)`, `branching on [start]`, minimising a variable.
**Run:** `savilerow jobshop.eprime jobshop.param -run-solver -solutions-to-stdout`
**Expected:** `letting makespan be 11`
