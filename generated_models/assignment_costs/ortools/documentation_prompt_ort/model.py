from ortools.sat.python import cp_model
import json

# Input data
cost = [
    [14, 5, 8, 7, 15],
    [2, 12, 6, 5, 3],
    [7, 8, 3, 9, 7],
    [2, 4, 6, 10, 1]
]

num_tasks = len(cost)
num_people = len(cost[0])

# Model definition
model = cp_model.CpModel()

# Decision Variables
# x[t][p] = 1 if task t is assigned to person p, 0 otherwise
x = []
for t in range(num_tasks):
    row = []
    for p in range(num_people):
        row.append(model.NewBoolVar(f'x_{t}_{p}'))
    x.append(row)

# Constraints
# Each task must be assigned to exactly one person
for t in range(num_tasks):
    model.Add(sum(x[t][p] for p in range(num_people)) == 1)

# Objective function: minimize total cost
total_cost = sum(x[t][p] * cost[t][p] for t in range(num_tasks) for p in range(num_people))
model.Minimize(total_cost)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x': [[solver.Value(x[t][p]) for p in range(num_people)] for t in range(num_tasks)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")