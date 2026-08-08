
import cpmpy as cp
import json

# Data
m = [
    [1, 1, 1, 1],
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1]
]

n_people = len(m)
n_slots = len(m[0])

# Model definition
model = cp.Model()

# Decision Variables
# x[i,j] = 1 if person i is assigned to slot j, else 0
x = cp.boolvar(shape=(n_people, n_slots), name="x")

# Constraints
# Each person is assigned to exactly one slot
for i in range(n_people):
    model += (cp.sum(x[i, :]) == 1)

# Each slot is assigned to exactly one person
for j in range(n_slots):
    model += (cp.sum(x[:, j]) == 1)

# Assign only if person is free at that slot
for i in range(n_people):
    for j in range(n_slots):
        model += (x[i, j] <= m[i][j])

# Solve and print
if model.solve():
    solution = {'x': x.value().astype(int).tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
