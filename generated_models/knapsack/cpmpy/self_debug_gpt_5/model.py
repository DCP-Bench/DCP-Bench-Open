
import cpmpy as cp
import json
import numpy as np

# Data (optional)
values = [4, 2, 3, 7, 1]  # Values of the items
weights = [3, 1, 2, 5, 4]  # Weights of the items
capacity = 7  # Capacity of the knapsack
# End of data

# Model definition
model = cp.Model()

# Decision Variables
n = len(values)
x = cp.boolvar(shape=n, name="x")  # 1 if item is taken, 0 otherwise

# Constraints
weights_arr = np.array(weights)
values_arr = np.array(values)
model += (cp.sum(weights_arr * x) <= capacity)

# Objective (optional)
model.maximize(cp.sum(values_arr * x))

# Solve and print
if model.solve():
    x_list = [int(v) for v in x.value().tolist()]
    solution = {'x': x_list}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
