
from ortools.sat.python import cp_model
import json

# Input data
m = [
    [1, 1, 1, 1],
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1]
]  # Matrix representing the free-busy schedules

# Model definition
model = cp_model.CpModel()

# Decision Variables: x[i][j] == 1 if person i is assigned to slot j
num_people = len(m)
num_slots = len(m[0])
x = [
    [model.NewBoolVar(f'x[{i}][{j}]') for j in range(num_slots)]
    for i in range(num_people)
]

# Each person is assigned to exactly one slot
for i in range(num_people):
    model.Add(sum(x[i][j] for j in range(num_slots)) == 1)

# Each slot has exactly one person
for j in range(num_slots):
    model.Add(sum(x[i][j] for i in range(num_people)) == 1)

# Respect free-busy constraints: x[i][j] <= m[i][j]
for i in range(num_people):
    for j in range(num_slots):
        model.Add(x[i][j] <= m[i][j])

# Objective: maximize the number of assignments (to ensure full matching if possible)
model.Maximize(sum(x[i][j] for i in range(num_people) for j in range(num_slots)))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x': [[solver.Value(x[i][j]) for j in range(num_slots)] for i in range(num_people)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
