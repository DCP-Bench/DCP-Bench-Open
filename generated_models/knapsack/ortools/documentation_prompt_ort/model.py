from ortools.sat.python import cp_model
import json

# Input data
values = [4, 2, 3, 7, 1]  # Values of the items
weights = [3, 1, 2, 5, 4]  # Weights of the items
capacity = 7  # Capacity of the knapsack
num_items = len(values)

# Model definition
model = cp_model.CpModel()

# Decision Variables: x[i] = 1 if item i is taken, 0 otherwise
x = [model.NewBoolVar(f'x{i}') for i in range(num_items)]

# Constraint: total weight of selected items must not exceed capacity
model.Add(sum(x[i] * weights[i] for i in range(num_items)) <= capacity)

# Objective: maximize total value of selected items
model.Maximize(sum(x[i] * values[i] for i in range(num_items)))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x': [solver.Value(x[i]) for i in range(num_items)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")