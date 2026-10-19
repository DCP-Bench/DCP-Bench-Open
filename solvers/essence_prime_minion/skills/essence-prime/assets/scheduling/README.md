# Resource-constrained project (scheduling, minimise the makespan)

**Problem:** six tasks with durations and resource demands share a resource of capacity 3; four precedences (given as an edge list); finish as early as possible.
**Shows:** `cumulative(starts, durations, demands, capacity)`, precedences read from a 2-D parameter matrix, a horizon computed with `letting horizon = sum(dur)`, comma-grouped `given`s, `branching on [start]` with `heuristic sdf` before the objective, minimising a maximum (`start[t] + dur[t] <= makespan`), an implied work bound that helps Minion prove the optimum.
**Run:** `savilerow rcpsp.eprime project.param -run-solver -solutions-to-stdout`
**Expected:** `letting makespan be 11`
**Expected:** `$ Minion SolverTimeOut: 0`
