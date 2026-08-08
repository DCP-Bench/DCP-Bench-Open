from ortools.sat.python import cp_model
import json

# Input data
m = [
    [1, 1, 1, 1],
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1]
]  # Matrix representing the free-busy schedules

num_people = len(m)
num_slots = len(m[0])

# Model definition
model = cp_model.CpModel()

# Decision Variables
# x[i][j] = 1 if person i is assigned to slot j, 0 otherwise
x = []
for i in range(num_people):
    row = []
    for j in range(num_slots):
        row.append(model.NewIntVar(0, 1, f'x_{i}_{j}'))
    x.append(row)

# Constraints

# Each person is assigned to exactly one slot
for i in range(num_people):
    model.Add(sum(x[i][j] for j in range(num_slots)) == 1)

# Each slot is assigned to exactly one person
for j in range(num_slots):
    model.Add(sum(x[i][j] for i in range(num_people)) == 1)

# Assignments must respect free-busy schedules (only assign if free)
for i in range(num_people):
    for j in range(num_slots):
        if m[i][j] == 0:
            model.Add(x[i][j] == 0)

# No objective function needed, just find a feasible assignment

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    assignment = []
    for i in range(num_people):
        assignment.append([solver.Value(x[i][j]) for j in range(num_slots)])
    solution = {'x': assignment}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")