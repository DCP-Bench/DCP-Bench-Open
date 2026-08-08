
import cpmpy as cp
import numpy as np
import json

# Data
cost = np.array([
    [14, 5, 8, 7, 15],
    [2, 12, 6, 5, 3],
    [7, 8, 3, 9, 7],
    [2, 4, 6, 10, 1]
])
# End of data

# Model definition
model = cp.Model()

# Decision Variables: x[t,p] = 1 if task t is assigned to person p
x = cp.boolvar(shape=cost.shape, name="x")

# Constraints
# Each task must be assigned to exactly one person
for t in range(cost.shape[0]):
    model += cp.sum(x[t, :]) == 1

# Objective: minimize total assignment cost
model.minimize(cp.sum(cost * x))

# Solve and print
if model.solve():
    solution = {
        'x': x.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
