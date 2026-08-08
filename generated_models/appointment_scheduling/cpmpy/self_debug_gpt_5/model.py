
import cpmpy as cp
import json
import numpy as np

# Data (optional)
m = [
    [1, 1, 1, 1],
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1]
]  # Matrix representing the free-busy schedules
# End of data

n_people = len(m)
n_slots = len(m[0])

# Model definition
model = cp.Model()

# Decision Variables
x = cp.boolvar(shape=(n_people, n_slots), name="x")  # x[i][j] = 1 if person i assigned to slot j

# Constraints
# Availability constraints: cannot assign if not available
for i in range(n_people):
    for j in range(n_slots):
        model += (x[i, j] <= m[i][j])

# Each person is assigned to exactly one slot
for i in range(n_people):
    model += (cp.sum(x[i, :]) == 1)

# Each slot is assigned to exactly one person
for j in range(n_slots):
    model += (cp.sum(x[:, j]) == 1)

# Objective (optional)

# Solve and print
if model.solve():
    solution = {'x': x.value().astype(int).tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
