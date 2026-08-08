from ortools.sat.python import cp_model
import json

# Input data
weights = [4, 3, 1, 3, 2, 5, 2]
capacity = 5
num_bins = 5
num_items = len(weights)

# Model definition
model = cp_model.CpModel()

# Decision Variables
# bins[i] is the bin assigned to item i
bins = [model.NewIntVar(0, num_bins - 1, f'bins_{i}') for i in range(num_items)]

# Constraints
# For each bin, the sum of weights of items assigned to it must not exceed capacity
for b in range(num_bins):
    # Create a boolean variable for each item indicating if it is in bin b
    in_bin = [model.NewBoolVar(f'in_bin_{b}_item_{i}') for i in range(num_items)]
    for i in range(num_items):
        # Link in_bin[i] with bins[i] == b
        model.Add(bins[i] == b).OnlyEnforceIf(in_bin[i])
        model.Add(bins[i] != b).OnlyEnforceIf(in_bin[i].Not())
    # Sum of weights of items in bin b
    model.Add(sum(in_bin[i] * weights[i] for i in range(num_items)) <= capacity)

# No objective function, just feasibility

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'bins': [solver.Value(b) for b in bins]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")