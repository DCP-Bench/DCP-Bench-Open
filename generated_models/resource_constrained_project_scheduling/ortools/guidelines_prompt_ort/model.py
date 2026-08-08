
from ortools.sat.python import cp_model
import json

# Input data
durations_data = [0, 3, 2, 5, 4, 2, 3, 4, 2, 4, 6, 0]
resource_needs_data = [
    [0, 0], [5, 1], [0, 4], [1, 4], [1, 3],
    [3, 2], [3, 1], [2, 4], [4, 0], [5, 2],
    [2, 5], [0, 0]
]
resource_capacities_data = [6, 8]
successors_link_data = [
    [0, 1], [0, 2], [0, 3], [1, 4], [1, 5],
    [2, 9], [2, 10], [3, 8], [4, 6], [4, 7],
    [5, 9], [5, 10], [6, 8], [6, 9], [7, 8],
    [8, 11], [9, 11], [10, 11]
]

# Compute horizon as sum of all durations
horizon = sum(durations_data)

# Model definition
model = cp_model.CpModel()

num_jobs = len(durations_data)
num_resources = len(resource_capacities_data)

# Decision Variables: start times and end times for each job
start_time = [
    model.NewIntVar(0, horizon, f"start_time[{j}]") for j in range(num_jobs)
]
end_time = [
    model.NewIntVar(0, horizon, f"end_time[{j}]") for j in range(num_jobs)
]

# Fix the start of the dummy initial job to 0
model.Add(start_time[0] == 0)

# Create intervals for all jobs
intervals = []
for j in range(num_jobs):
    intervals.append(
        model.NewIntervalVar(
            start_time[j],
            durations_data[j],
            end_time[j],
            f"interval_{j}"
        )
    )

# Precedence constraints
for pred, succ in successors_link_data:
    model.Add(start_time[succ] >= end_time[pred])

# Resource constraints: cumulative for each resource type
for r in range(num_resources):
    demands = [resource_needs_data[j][r] for j in range(num_jobs)]
    model.AddCumulative(intervals, demands, resource_capacities_data[r])

# Makespan variable (maximum of all end times)
makespan = model.NewIntVar(0, horizon, "makespan")
model.AddMaxEquality(makespan, end_time)

# Objective: minimize makespan
model.Minimize(makespan)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Output the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'start_time': [solver.Value(start_time[j]) for j in range(num_jobs)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
