
from ortools.sat.python import cp_model
import json

# Input data
num_people = 8  # number of people
# 1-based indexing: compatible[i] is the list of people to which person (i+1) can donate
compatible = [
    [2, 3],
    [1, 6],
    [1, 4, 7],
    [2],
    [2],
    [5],
    [8],
    [3]
]

# Model definition
model = cp_model.CpModel()

# Decision Variables
# transplants[i][j] = 1 if person (i+1) donates to person (j+1), else 0
transplants = []
for i in range(num_people):
    row = []
    for j in range(num_people):
        var = model.NewBoolVar(f"t_{i}_{j}")
        # If j+1 not in compatible[i], force var to 0
        if (j + 1) not in compatible[i]:
            model.Add(var == 0)
        row.append(var)
    transplants.append(row)

# Constraints
# 1. Each person donates at most one kidney
for i in range(num_people):
    model.Add(sum(transplants[i][j] for j in range(num_people)) <= 1)

# 2. Conservation: a person who donates must also receive exactly one kidney
#    and vice versa: sum_out(i) == sum_in(i)
for i in range(num_people):
    out_flow = sum(transplants[i][j] for j in range(num_people))
    in_flow = sum(transplants[j][i] for j in range(num_people))
    model.Add(out_flow == in_flow)

# Objective: maximize the total number of transplants
model.Maximize(sum(transplants[i][j] for i in range(num_people) for j in range(num_people)))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    result = []
    for i in range(num_people):
        row = []
        for j in range(num_people):
            row.append(solver.Value(transplants[i][j]))
        result.append(row)
    solution = {
        'transplants': result
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
