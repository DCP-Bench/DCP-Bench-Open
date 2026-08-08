
import cpmpy as cp
import json

# Data
base = 6  # Side length of the large square
sides = [3, 3, 3, 2, 1, 1, 1, 1, 1]  # Side lengths of the smaller squares
n = len(sides)
# End of data

# Model definition
model = cp.Model()

# Decision Variables: x and y coordinates for the bottom-left corner of each small square
x_coords = cp.intvar(0, base, shape=n, name="x_coords")
y_coords = cp.intvar(0, base, shape=n, name="y_coords")

# Constraints
# Each square must be inside the large square
for i in range(n):
    model += x_coords[i] + sides[i] <= base
    model += y_coords[i] + sides[i] <= base

# Non-overlap constraints: for each pair of squares, at least one separating axis holds
for i in range(n):
    for j in range(i + 1, n):
        model += (
            (x_coords[i] + sides[i] <= x_coords[j])
            | (x_coords[j] + sides[j] <= x_coords[i])
            | (y_coords[i] + sides[i] <= y_coords[j])
            | (y_coords[j] + sides[j] <= y_coords[i])
        )

# (No objective: just find any feasible perfect packing)

# Solve and print
if model.solve():
    solution = {
        'x_coords': x_coords.value().tolist(),
        'y_coords': y_coords.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
