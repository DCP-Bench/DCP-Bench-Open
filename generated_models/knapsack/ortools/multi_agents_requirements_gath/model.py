import json
from ortools.sat.python import cp_model

# ------------------ Input Data ------------------
values = [4, 2, 3, 7, 1]  # Values of the items
weights = [3, 1, 2, 5, 4]  # Weights of the items
capacity = 7  # Capacity of the knapsack

# ------------------ Model ------------------
model = cp_model.CpModel()
num_items = len(values)

# Decision variables: x[i] = 1 if item i is selected, 0 otherwise.
x = [model.NewBoolVar(f"x[{i}]") for i in range(num_items)]

# Capacity constraint: total weight cannot exceed capacity.
model.Add(sum(weights[i] * x[i] for i in range(num_items)) <= capacity)

# Objective: maximize total value.
model.Maximize(sum(values[i] * x[i] for i in range(num_items)))

# ------------------ Solve ------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# ------------------ Output ------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    x_solution = [int(solver.Value(var)) for var in x]
else:
    x_solution = [0] * num_items  # Fallback (should not happen with given data)

print(json.dumps({"x": x_solution}))