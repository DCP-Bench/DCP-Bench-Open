
import cpmpy as cp
import json

# Data
jobs_data = [  # (machine_id, duration)
    [(0, 3), (1, 2), (2, 2)],  # Job 0
    [(0, 2), (2, 1), (1, 4)],  # Job 1
    [(1, 4), (2, 3)]           # Job 2
]
# End of data

# Compute horizon (upper bound on makespan)
horizon = sum(d for job in jobs_data for (_, d) in job)

# Number of jobs
num_jobs = len(jobs_data)

# Model definition
model = cp.Model()

# Decision Variables
# start[j][t] = start time of task t of job j
start = [
    [cp.IntVar(0, horizon, f"start_{j}_{t}") for t in range(len(jobs_data[j]))]
    for j in range(num_jobs)
]
# makespan variable
makespan = cp.IntVar(0, horizon, "makespan")

# Constraints
# 1. Precedence constraints within each job
for j in range(num_jobs):
    for t in range(len(jobs_data[j]) - 1):
        dur = jobs_data[j][t][1]
        model += (start[j][t] + dur <= start[j][t + 1])

# 2. Machine capacity constraints using cumulative (no overlap)
# For each machine, collect the tasks assigned to it
all_machines = set(m for job in jobs_data for (m, _) in job)
for m in all_machines:
    starts_m = []
    durations_m = []
    demands_m = []
    for j in range(num_jobs):
        for t, (machine_id, dur) in enumerate(jobs_data[j]):
            if machine_id == m:
                starts_m.append(start[j][t])
                durations_m.append(dur)
                demands_m.append(1)
    # capacity 1 => at most one task at a time on machine m
    model += cp.cumulative(starts_m, durations_m, demands_m, 1)

# 3. Define makespan: all tasks must finish by makespan
for j in range(num_jobs):
    for t, (_, dur) in enumerate(jobs_data[j]):
        model += (start[j][t] + dur <= makespan)

# Objective: minimize makespan
model.minimize(makespan)

# Solve and print
if model.solve():
    solution = {'makespan': int(makespan.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
