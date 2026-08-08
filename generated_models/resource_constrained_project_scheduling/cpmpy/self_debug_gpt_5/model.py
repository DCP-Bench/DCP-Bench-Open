
import cpmpy as cp
import json
import numpy as np

# Data
durations_data = [0, 3, 2, 5, 4, 2, 3, 4, 2, 4, 6, 0]
resource_needs_data = [[0, 0], [5, 1], [0, 4], [1, 4], [1, 3], [3, 2], [3, 1], [2, 4], [4, 0], [5, 2], [2, 5], [0, 0]]
resource_capacities_data = [6, 8]
successors_link_data = [[0, 1], [0, 2], [0, 3], [1, 4], [1, 5], [2, 9], [2, 10], [3, 8], [4, 6], [4, 7], [5, 9], [5, 10], [6, 8], [6, 9], [7, 8], [8, 11], [9, 11], [10, 11]]
# End of data

# Derived data
n_jobs = len(durations_data)
n_res = len(resource_capacities_data)
durations_np = np.array(durations_data, dtype=int)
horizon = int(sum(durations_data))  # safe upper bound on makespan
sink_job = n_jobs - 1  # assuming last job is the sink

# Model definition
model = cp.Model()

# Decision Variables
start_time = cp.intvar(0, horizon, shape=n_jobs, name="start_time")
end_time = cp.intvar(0, horizon, shape=n_jobs, name="end_time")

# Constraints

# Link start and end times with durations
model += (end_time == start_time + durations_np)

# Precedence constraints
for i, j in successors_link_data:
    model += (start_time[j] >= end_time[i])

# Resource capacity constraints (cumulative for each resource)
for r in range(n_res):
    demands_r = np.array([resource_needs_data[j][r] for j in range(n_jobs)], dtype=int)
    model += cp.Cumulative(start_time, durations_np, end_time, demands_r, resource_capacities_data[r])

# Objective: minimize makespan (end time of sink job)
model.minimize(end_time[sink_job])

# Solve and print
if model.solve():
    solution = {'start_time': start_time.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
