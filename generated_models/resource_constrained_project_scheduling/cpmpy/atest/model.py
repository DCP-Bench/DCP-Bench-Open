from cpmpy import *
import json

# Input data
durations_data = [0, 3, 2, 5, 4, 2, 3, 4, 2, 4, 6, 0]
resource_needs_data = [[0, 0], [5, 1], [0, 4], [1, 4], [1, 3], [3, 2], [3, 1], [2, 4], [4, 0], [5, 2], [2, 5], [0, 0]]
resource_capacities_data = [6, 8]
successors_link_data = [[0, 1], [0, 2], [0, 3], [1, 4], [1, 5], [2, 9], [2, 10], [3, 8], [4, 6], [4, 7], [5, 9], [5, 10], [6, 8], [6, 9], [7, 8], [8, 11], [9, 11], [10, 11]]

# Number of jobs and resources
num_jobs = len(durations_data)
num_resources = len(resource_capacities_data)

# Maximum possible makespan (sum of all durations)
max_duration = sum(durations_data)

# Decision variables
# start_time[j]: start time of job j
start_time = intvar(0, max_duration, shape=num_jobs, name="start_time")

# Model
model = Model()

# Constraint: Precedence constraints
for (i, j) in successors_link_data:
    model += [start_time[j] >= start_time[i] + durations_data[i]]

# Constraint: Resource capacities
for r in range(num_resources):
    # For each pair of jobs, ensure that their resource usage does not overlap in a way that exceeds capacity
    for j1 in range(num_jobs):
        for j2 in range(j1 + 1, num_jobs):
            # If jobs j1 and j2 use resource r, ensure they do not overlap
            if resource_needs_data[j1][r] > 0 and resource_needs_data[j2][r] > 0:
                model += (start_time[j1] + durations_data[j1] <= start_time[j2]) | \
                         (start_time[j2] + durations_data[j2] <= start_time[j1])

# Objective: Minimize the makespan (end time of the last job)
makespan = intvar(0, max_duration, name="makespan")
model += [makespan >= start_time[j] + durations_data[j] for j in range(num_jobs)]
model.minimize(makespan)

# Solve the model
model.solve()

# Print the solution
solution = {"start_time": start_time.value().tolist()}
print(json.dumps(solution))