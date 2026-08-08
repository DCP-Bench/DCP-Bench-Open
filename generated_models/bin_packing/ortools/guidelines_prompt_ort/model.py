
from ortools.sat.python import cp_model
import json

# Input data
weights = [4, 3, 1, 3, 2, 5, 2]
capacity = 5
num_bins = 5
num_items = len(weights)

# Model definition
model = cp_model.CpModel()

# Decision variables
# bins[i] is the bin index to which item i is assigned
bins = [model.NewIntVar(0, num_bins - 1, f'bins[{i}]') for i in range(num_items)]

# Auxiliary boolean variables assign[i][j] = 1 if item i is in bin j
assign = []
for i in range(num_items):
    row = []
    for j in range(num_bins):
        b = model.NewBoolVar(f'assign[{i},{j}]')
        row.append(b)
        # Link bins[i] and assign[i][j]
        model.Add(bins[i] == j).OnlyEnforceIf(b)
        model.Add(bins[i] != j).OnlyEnforceIf(b.Not())
    assign.append(row)
    # Each item must be assigned to exactly one bin
    model.Add(sum(assign[i][j] for j in range(num_bins)) == 1)

# Capacity constraints: total weight in each bin <= capacity
for j in range(num_bins):
    model.Add(
        sum(weights[i] * assign[i][j] for i in range(num_items))
        <= capacity
    )

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'bins': [solver.Value(bins[i]) for i in range(num_items)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
