
from ortools.sat.python import cp_model
import json

# Input data
cost = [
    [14, 5, 8, 7, 15],
    [2, 12, 6, 5, 3],
    [7, 8, 3, 9, 7],
    [2, 4, 6, 10, 1]
]

# Create the model
model = cp_model.CpModel()

# Decision variables: x[t, p] = 1 if task t is assigned to person p
num_tasks = len(cost)
num_people = len(cost[0])
x = {}
for t in range(num_tasks):
    for p in range(num_people):
        x[(t, p)] = model.NewBoolVar(f"x[{t},{p}]")

# Each task must be assigned to exactly one person
for t in range(num_tasks):
    model.Add(sum(x[(t, p)] for p in range(num_people)) == 1)

# Objective: minimize total assignment cost
model.Minimize(
    sum(cost[t][p] * x[(t, p)] for t in range(num_tasks) for p in range(num_people))
)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    x_matrix = [
        [solver.Value(x[(t, p)]) for p in range(num_people)]
        for t in range(num_tasks)
    ]
    solution = {
        "x": x_matrix
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
