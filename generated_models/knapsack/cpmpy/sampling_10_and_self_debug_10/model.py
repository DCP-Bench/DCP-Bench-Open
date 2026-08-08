
import cpmpy as cp
import json

# Data
values = [4, 2, 3, 7, 1]
weights = [3, 1, 2, 5, 4]
capacity = 7

# Model definition
model = cp.Model()

# Decision Variables: x[i] = 1 if item i is taken, 0 otherwise
x = cp.boolvar(shape=len(values), name="x")

# Constraints
model += (cp.sum([x[i] * weights[i] for i in range(len(weights))]) <= capacity)

# Objective: maximize total value
model.maximize(cp.sum([x[i] * values[i] for i in range(len(values))]))

# Solve and print
if model.solve():
    solution = {'x': [int(val) for val in x.value().tolist()]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
