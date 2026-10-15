Jobshop: jobs are sequences of tasks, each task on a given machine with a given duration.

- Job j's tasks must run in the given order: a task starts after the previous task of its job completes. -> start_j_k + d_j_k <= start_j_(k+1) (integers as binary bits, PB comparison)
- A machine can only work on one task at a time: for every pair of tasks on the same machine, one finishes before the other starts. -> selector Bool per pair, If(sel, end_a <= start_b), If(~sel, end_b <= start_a)
- A task, once started, must run to completion: fixed duration, end = start + duration (built into the precedence and no-overlap constraints).
- Start times are integers in [0, horizon], horizon = sum of all durations (bounds any schedule). Encoding: binary bits, value = sum 2^k * bit (wide range, comparisons between tasks).
- Makespan: integer in [0, horizon]; every job's last task ends no later than the makespan. -> end_last_j <= makespan
- Objective: minimise the makespan (the output "makespan"; objective is the same expression).
