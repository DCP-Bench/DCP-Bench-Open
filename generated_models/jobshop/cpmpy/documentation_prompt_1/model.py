
import cpmpy as cp
import json
import numpy as np

# Data
jobs_data = [  # (machine_id, duration)
    [(0, 3), (1, 2), (2, 2)],  # Job 0
    [(0, 2), (2, 1), (1, 4)],  # Job 1
    [(1, 4), (2, 3)]           # Job 2
]
# End of data

# Extract problem parameters
num_jobs = len(jobs_data)
num_tasks_per_job = [len(job) for job in jobs_data]
machines = set()
for job in jobs_data:
    for (m, d) in job:
        machines.add(m)
machines = sorted(machines)
num_machines = len(machines)

# Flatten tasks and create indexing for tasks by machine
# We will create variables for start times of each task
# Also, we need to enforce machine constraints (no overlap on same machine)
# and job constraints (task order)

# Compute horizon (upper bound on makespan)
horizon = sum(d for job in jobs_data for (_, d) in job)

# Decision variables: start times for each task
start_times = []
for j in range(num_jobs):
    start_times.append([cp.intvar(0, horizon, name=f"s_{j}_{t}") for t in range(num_tasks_per_job[j])])

# Makespan variable
makespan = cp.intvar(0, horizon, name="makespan")

model = cp.Model()

# Constraints

# 1) Precedence constraints within each job
for j in range(num_jobs):
    for t in range(num_tasks_per_job[j] - 1):
        dur = jobs_data[j][t][1]
        model += (start_times[j][t] + dur <= start_times[j][t+1])

# 2) Machine constraints: no overlap of tasks on the same machine
# For each machine, collect all tasks that run on it
for m in machines:
    # Collect tasks on machine m: (job, task, start_var, duration)
    tasks_on_machine = []
    for j in range(num_jobs):
        for t in range(num_tasks_per_job[j]):
            machine_id, dur = jobs_data[j][t]
            if machine_id == m:
                tasks_on_machine.append((j, t, start_times[j][t], dur))
    # Add disjunctive constraints: for each pair of tasks on the same machine, one must finish before the other starts
    for i in range(len(tasks_on_machine)):
        for k in range(i+1, len(tasks_on_machine)):
            j1, t1, s1, d1 = tasks_on_machine[i]
            j2, t2, s2, d2 = tasks_on_machine[k]
            # Either s1 + d1 <= s2 or s2 + d2 <= s1
            model += ( (s1 + d1 <= s2) | (s2 + d2 <= s1) )

# 3) Makespan constraints: makespan >= finish time of every task
for j in range(num_jobs):
    for t in range(num_tasks_per_job[j]):
        dur = jobs_data[j][t][1]
        model += (makespan >= start_times[j][t] + dur)

# Objective: minimize makespan
model.minimize(makespan)

# Solve and print
if model.solve():
    solution = {'makespan': int(makespan.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
