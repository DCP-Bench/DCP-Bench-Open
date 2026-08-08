
import cpmpy as cp
import json

m = [
    [1, 1, 1, 1],
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1]
]

model = cp.Model()

# Decision Variables: 4x4 matrix of boolean variables
x = cp.boolvar(shape=(4, 4), name="x")

# Constraints
# Each person must be assigned to exactly one slot
for i in range(4):
    model += cp.sum(x[i, :]) == 1

# Each slot must have exactly one person
for j in range(4):
    model += cp.sum(x[:, j]) == 1

# Assignments must respect free-busy schedules
for i in range(4):
    for j in range(4):
        model += x[i, j] <= m[i][j]

# Solve and print
if model.solve():
    # Convert boolean values to integers (0/1) for JSON
    x_val = x.value().tolist()
    solution = {'x': [[int(v) for v in row] for row in x_val]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
