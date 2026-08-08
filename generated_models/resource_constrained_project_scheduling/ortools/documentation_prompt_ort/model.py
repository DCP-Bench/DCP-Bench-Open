from ortools.sat.python import cp_model
import json

# Input data
durations_data = [0, 3, 2, 5, 4, 2, 3, 4, 2, 4, 6, 0]
resource_needs_data = [
    [0, 0], [5, 1], [0, 4], [1, 4], [1, 3], [3, 2], [3, 1], [2, 4], [4, 0], [5, 2], [2, 5], [0, 0]
]
resource_capacities_data = [6, 8]
successors_link_data = [
    [0, 1], [0, 2], [0, 3], [1, 4], [1, 5], [2, 9], [2, 10], [3, 8], [4, 6], [4, 7], [5, 9], [5, 10],
    [6, 8], [6, 9], [7, 8], [8, 11], [9, 11], [10, 11]
]

num_jobs = len(durations_data)
num_resources = len(resource_capacities_data)

# Model definition
model = cp_model.CpModel()

# Horizon is the sum of all durations (upper bound on project length)
horizon = sum(durations_data)

# Decision variables: start times of jobs
start_time = [model.NewIntVar(0, horizon, f'start_time_{j}') for j in range(num_jobs)]

# Create interval variables for each job (start, duration, end)
intervals = []
for j in range(num_jobs):
    intervals.append(model.NewIntervalVar(start_time[j], durations_data[j], start_time[j] + durations_data[j], f'interval_{j}'))

# Precedence constraints: for each successor link, predecessor must finish before successor starts
for pred, succ in successors_link_data:
    model.Add(start_time[succ] >= start_time[pred] + durations_data[pred])

# Resource constraints: cumulative for each resource
for r in range(num_resources):
    demands = [resource_needs_data[j][r] for j in range(num_jobs)]
    # Only consider jobs with positive demand for this resource
    intervals_with_demand = []
    demands_filtered = []
    for j in range(num_jobs):
        if demands[j] > 0:
            intervals_with_demand.append(intervals[j])
            demands_filtered.append(demands[j])
    if intervals_with_demand:
        model.AddCumulative(intervals_with_demand, demands_filtered, resource_capacities_data[r])

# Objective: minimize makespan (max end time)
makespan = model.NewIntVar(0, horizon, 'makespan')
ends = [start_time[j] + durations_data[j] for j in range(num_jobs)]
model.AddMaxEquality(makespan, ends)
model.Minimize(makespan)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {'start_time': [solver.Value(start_time[j]) for j in range(num_jobs)]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")