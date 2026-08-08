
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

# Horizon: sum of all durations (upper bound for scheduling)
horizon = sum(durations_data)

# Model definition
model = cp.Model()

# Decision Variables
# Start times for each job (0-based)
start_time = cp.intvar(0, horizon, shape=n_jobs, name="start_time")

# Makespan variable (end of project)
makespan = cp.intvar(0, horizon, name="makespan")

# Constraints

# 1) Precedence constraints: successor start >= predecessor start + predecessor duration
for pred, succ in successors_link_data:
    model += (start_time[succ] >= start_time[pred] + durations_data[pred])

# 2) Makespan is at least the finish time of each job
for j in range(n_jobs):
    model += (makespan >= start_time[j] + durations_data[j])

# 3) Resource capacity constraints at each time point
# We use a time-indexed approach: for each time unit, sum of resource usage of active jobs <= capacity
# To reduce complexity, only check times where jobs can be active (0..horizon-1)
for t in range(horizon):
    for r in range(n_resources):
        # Sum resource usage of jobs active at time t for resource r
        # A job j is active at time t if start_time[j] <= t < start_time[j] + durations[j]
        # We use reified constraints to model this
        active_jobs = []
        for j in range(n_jobs):
            if durations_data[j] > 0:
                # Boolean variable: is job j active at time t?
                active = cp.boolvar()
                model += (active == ((start_time[j] <= t) & (t < start_time[j] + durations_data[j])))
                active_jobs.append(active * resource_needs_data[j][r])
            else:
                # Jobs with zero duration do not consume resources
                pass
        if active_jobs:
            model += (cp.sum(active_jobs) <= resource_capacities_data[r])

# Objective: minimize makespan
model.minimize(makespan)

# Solve and print
if model.solve():
    solution = {'start_time': start_time.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
