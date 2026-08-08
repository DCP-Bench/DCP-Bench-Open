
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
# End of data

# Model definition
model = cp.Model()

# Decision Variables: x[i][j] is True if person i assigned to slot j
x = cp.boolvar(shape=(n_people, n_slots), name="x")

# Constraints
# Each person is assigned to exactly one slot
for i in range(n_people):
    model += (cp.sum(x[i, :]) == 1)

# Each slot has exactly one person
for j in range(n_slots):
    model += (cp.sum(x[:, j]) == 1)

# Respect availability: if m[i][j] == 0 then x[i][j] must be False
for i in range(n_people):
    for j in range(n_slots):
        if m[i][j] == 0:
            model += (x[i, j] == 0)

# Solve and print
if model.solve():
    x_val = x.value().tolist()
    # Convert booleans to 0/1 integers as required
    x_int = [[int(cell) for cell in row] for row in x_val]
    solution = {'x': x_int}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
