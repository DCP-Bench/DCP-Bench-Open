from cpmpy import *
import json

# Parameters
durations_data = [0, 3, 2, 5, 4, 2, 3, 4, 2, 4, 6, 0]
resource_needs_data = [[0, 0], [5, 1], [0, 4], [1, 4], [1, 3], [3, 2], [3, 1], [2, 4], [4, 0], [5, 2], [2, 5], [0, 0]]
resource_capacities_data = [6, 8]
successors_link_data = [[0, 1], [0, 2], [0, 3], [1, 4], [1, 5], [2, 9], [2, 10], [3, 8], [4, 6], [4, 7], [5, 9], [5, 10], [6, 8], [6, 9], [7, 8], [8, 11], [9, 11], [10, 11]]
n_jobs = len(durations_data)
n_resources = len(resource_capacities_data)

# Decision Variables
max_time = sum(durations_data)  # Upper bound for makespan
start_time = intvar(0, max_time, shape=n_jobs, name="start_time")
makespan = intvar(0, max_time, name="makespan")

# Model
model = Model()

# Constraint: makespan is the maximum end time of all jobs
end_times = [start_time[i] + durations_data[i] for i in range(n_jobs)]
model += makespan == max(end_times)

# Constraint: precedence constraints
for (pred, succ) in successors_link_data:
    model += start_time[succ] >= start_time[pred] + durations_data[pred]

# Constraint: resource capacity constraints
for r in range(n_resources):
    # Create lists of start times, durations and demands for this resource
    starts = []
    durations = []
    demands = []
    for j in range(n_jobs):
        if resource_needs_data[j][r] > 0:
            starts.append(start_time[j])
            durations.append(durations_data[j])
            demands.append(resource_needs_data[j][r])
    
    # Add cumulative constraint for this resource
    if starts and demands:
        model += cumulative(starts, durations, demands, resource_capacities_data[r])

# Objective: minimize makespan
model.minimize(makespan)

# Solve
model.solve()

# Print solution
solution = {
    "start_time": start_time.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script