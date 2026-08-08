
import cpmpy as cp
import json

# Data
m = [
    [1, 1, 1, 1],
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1]
]
# End of data

# Model definition
model = cp.Model()

# Decision Variables: x[i][j] = 1 if person i is assigned to slot j
x = cp.intvar(0, 1, shape=(4, 4), name="x")

# Constraints
# Each person is assigned to exactly one slot
for i in range(4):
    model += cp.sum(x[i, :]) == 1

# Each slot has exactly one person
for j in range(4):
    model += cp.sum(x[:, j]) == 1

# Respect free-busy matrix: if m[i][j] == 0 then x[i][j] == 0
for i in range(4):
    for j in range(4):
        if m[i][j] == 0:
            model += x[i, j] == 0

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
