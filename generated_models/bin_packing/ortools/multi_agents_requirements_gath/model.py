import json
from ortools.sat.python import cp_model

# --------------------------------------------------
# Input data (exactly as provided – do not modify)
# --------------------------------------------------
weights = [4, 3, 1, 3, 2, 5, 2]
capacity = 5
num_bins = 5
n_items = len(weights)

# --------------------------------------------------
# Model
# --------------------------------------------------
model = cp_model.CpModel()

# x[i][j] is True if item i is placed in bin j
x = [[model.NewBoolVar(f"x_{i}_{j}") for j in range(num_bins)] for i in range(n_items)]

# Each item must be assigned to exactly one bin
for i in range(n_items):
    model.Add(sum(x[i][j] for j in range(num_bins)) == 1)

# Capacity constraint for every bin
for j in range(num_bins):
    model.Add(sum(weights[i] * x[i][j] for i in range(n_items)) <= capacity)

# Pure feasibility problem – no optimisation needed

# --------------------------------------------------
# Solve
# --------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# --------------------------------------------------
# Extract and output solution
# --------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    bins = []
    for i in range(n_items):
        # Find the bin j where x[i][j] is True
        for j in range(num_bins):
            if solver.BooleanValue(x[i][j]):
                bins.append(j)
                break
    print(json.dumps({"bins": bins}))
else:
    # If no solution is found, output an empty assignment (still valid JSON)
    print(json.dumps({"bins": []}))
