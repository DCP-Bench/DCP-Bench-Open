Job shop: multiple jobs are processed on several machines; minimise the makespan.
-> class JobShop, reads jobs_data (job -> ordered list of [machine, duration]).

Each job consists of a sequence of tasks, which must be performed in a given order
-> rel(*this, start[t] + dur[t] <= start[t+1]) for consecutive tasks of a job (no map row; a fixed-offset precedence is linear).

each task must be processed on a specific machine
-> tasks grouped per machine from the data (machine index read from the instance).

A machine can only work on one task at a time
-> unary(*this, starts of the machine's tasks, IntArgs(durations of the machine's tasks)) per machine (IPL default; disjunctive reasoning is the unary propagator).

A task, once started, must run to completion
-> fixed durations on the unary; no preemption is possible by construction (no extra post).

the time it takes for all the jobs to be completed
-> end[t] = start[t] + dur[t] (expr); makespan = max(end) -> max(*this, ends, makespan) with makespan in 0..horizon.

branching (decision variables are the task start times, horizon = sum of all durations from the data)
-> restarts(100); branch(*this, starts, INT_VAR_AFC_SIZE_MAX(0.99), INT_VAL_SPLIT_MIN()). Attempt 1 with INT_VAR_MIN_MIN/INT_VAL_MIN and no restarts ended after one solution (suboptimal_solution on ft06); see lessons.md.

objective: minimise the makespan
-> minimize(makespan).
