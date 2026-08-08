
import cpmpy as cp
import json
import numpy as np

# Data
durations_data = [0, 3, 2, 5, 4, 2, 3, 4, 2, 4, 6, 0]
resource_needs_data = [[0, 0], [5, 1], [0, 4], [1, 4], [1, 3], [3, 2], [3, 1], [2, 4], [4, 0], [5, 2], [2, 5], [0, 0]]
resource_capacities_data = [6, 8]
successors_link_data = [[0, 1], [0, 2], [0, 3], [1, 4], [1, 5], [2, 9], [2, 10], [3, 8], [4, 6], [4, 7], [5, 9], [5, 10], [6, 8], [6, 9], [7, 8], [8, 11], [9, 11], [10, 11]]

# Number of jobs and resources
n_jobs = len(durations_data)
n_resources = len(resource_capacities_data)

# Compute an upper bound for the schedule horizon (sum of all durations)
horizon = sum(durations_data)

# Model definition
model = cp.Model()

# Decision Variables
# Start times for each job (0 <= start_time <= horizon)
start_time = cp.intvar(0, horizon, shape=n_jobs, name="start_time")

# Makespan variable (end of project)
makespan = cp.intvar(0, horizon, name="makespan")

# Boolean variables active[j][t] indicating if job j is active at time t
active = cp.boolvar(shape=(n_jobs, horizon), name="active")

# Constraints

# 1) Precedence constraints: for each (pred, succ), start_succ >= start_pred + duration_pred
for pred, succ in successors_link_data:
    model += start_time[succ] >= start_time[pred] + durations_data[pred]

# 2) Makespan constraints: makespan >= start_time[job] + duration[job] for all jobs
for j in range(n_jobs):
    model += makespan >= start_time[j] + durations_data[j]

# 3) Link active variables with start_time and durations
for j in range(n_jobs):
    dur = durations_data[j]
    for t in range(horizon):
        in_start = cp.boolvar()
        in_end = cp.boolvar()
        # Enforce equivalences
        model += (in_start == (start_time[j] <= t))
        model += (in_end == (t < start_time[j] + dur))
        model += (active[j, t] == (in_start & in_end))

# 4) Resource capacity constraints at each time t for each resource r
for t in range(horizon):
    for r in range(n_resources):
        model += cp.sum([resource_needs_data[j][r] * active[j, t] for j in range(n_jobs)]) <= resource_capacities_data[r]

# Objective: minimize makespan
model.minimize(makespan)

# Solve and print
if model.solve():
    solution = {'start_time': start_time.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
