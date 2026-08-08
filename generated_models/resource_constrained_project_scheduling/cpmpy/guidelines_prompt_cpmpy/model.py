
import cpmpy as cp
import json

# Data
durations_data = [0, 3, 2, 5, 4, 2, 3, 4, 2, 4, 6, 0]
resource_needs_data = [
    [0, 0], [5, 1], [0, 4], [1, 4], [1, 3], [3, 2],
    [3, 1], [2, 4], [4, 0], [5, 2], [2, 5], [0, 0]
]
resource_capacities_data = [6, 8]
successors_link_data = [
    [0, 1], [0, 2], [0, 3], [1, 4], [1, 5], [2, 9], [2, 10],
    [3, 8], [4, 6], [4, 7], [5, 9], [5, 10], [6, 8],
    [6, 9], [7, 8], [8, 11], [9, 11], [10, 11]
]
# End of data

# Compute horizon as sum of all durations
horizon = sum(durations_data)

# Model definition
model = cp.Model()

# Number of jobs
n_jobs = len(durations_data)

# Decision Variables: start times for each job
start_time = cp.IntVar(0, horizon, shape=n_jobs, name="start_time")

# Makespan variable
makespan = cp.IntVar(0, horizon, name="makespan")

# Precedence constraints
for i, j in successors_link_data:
    model += (start_time[j] >= start_time[i] + durations_data[i])

# Define makespan = max_i (start_time[i] + durations_data[i])
model += (makespan == cp.max([start_time[i] + durations_data[i] for i in range(n_jobs)]))

# Resource constraints: cumulative for each resource
for r in range(len(resource_capacities_data)):
    demands = [resource_needs_data[i][r] for i in range(n_jobs)]
    model += cp.cumulative(start_time, durations_data, demands, resource_capacities_data[r])

# Objective: minimize makespan
model.minimize(makespan)

# Solve and print
if model.solve():
    solution = {'start_time': start_time.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
