import json
from ortools.sat.python import cp_model

# -----------------------
# 1. Input Data (immutable)
# -----------------------
# Availability matrix: m[i][j] = 1 if person i is free in slot j, 0 otherwise.
m = [
    [1, 1, 1, 1],
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1]
]

num_people = len(m)
num_slots = len(m[0])

# -----------------------
# 2. CP-SAT Model
# -----------------------
model = cp_model.CpModel()

# Decision variables: x[i][j] = 1 if person i is assigned to slot j
x = [
    [model.NewBoolVar(f"x[{i}][{j}]") for j in range(num_slots)]
    for i in range(num_people)
]

# -----------------------
# 3. Constraints
# -----------------------
# C1. Respect availability
for i in range(num_people):
    for j in range(num_slots):
        if m[i][j] == 0:
            # If not available, force variable to 0
            model.Add(x[i][j] == 0)

# C2. Each person is assigned to exactly one slot
for i in range(num_people):
    model.Add(sum(x[i][j] for j in range(num_slots)) == 1)

# C3. Each slot has exactly one person
for j in range(num_slots):
    model.Add(sum(x[i][j] for i in range(num_people)) == 1)

# No objective function (feasibility problem)

# -----------------------
# 4. Solve
# -----------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# -----------------------
# 5. Extract and print solution
# -----------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution_matrix = [
        [int(solver.Value(x[i][j])) for j in range(num_slots)]
        for i in range(num_people)
    ]
    print(json.dumps({"x": solution_matrix}))
else:
    # Infeasible or unknown -> print empty result structure
    print(json.dumps({"x": []}))
