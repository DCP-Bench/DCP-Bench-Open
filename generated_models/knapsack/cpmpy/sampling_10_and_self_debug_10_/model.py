
import cpmpy as cp
import json

# Data
values = [4, 2, 3, 7, 1]  # Values of the items
weights = [3, 1, 2, 5, 4]  # Weights of the items
capacity = 7  # Capacity of the knapsack
n = len(values)
# End of data

# Model definition
model = cp.Model()

# Decision Variables: x[i] = 1 if item i is taken, 0 otherwise
x = cp.boolvar(shape=n, name="x")

# Constraints: total weight must not exceed capacity
model += cp.sum([weights[i] * x[i] for i in range(n)]) <= capacity

# Objective: maximize total value
model.maximize(cp.sum([values[i] * x[i] for i in range(n)]))

# Solve and print
if model.solve():
    # convert boolean values to integers (0/1) as required
    solution = {'x': [int(v) for v in x.value().tolist()]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
