
import cpmpy as cp
import numpy as np
import json

# Data (optional)
cost = [
    [14, 5, 8, 7, 15],
    [2, 12, 6, 5, 3],
    [7, 8, 3, 9, 7],
    [2, 4, 6, 10, 1]
]
cost = np.array(cost, dtype=int)
num_tasks, num_people = cost.shape
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.boolvar(shape=(num_tasks, num_people), name="x")

# Constraints
# Each task assigned to exactly one person
for i in range(num_tasks):
    model += (cp.sum(x[i, :]) == 1)

# Each person assigned to at most one task (not all people need to be assigned)
for j in range(num_people):
    model += (cp.sum(x[:, j]) <= 1)

# Objective (optional)
model.minimize(cp.sum(cost * x))

# Solve and print
if model.solve():
    solution = {'x': x.value().astype(int).tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
