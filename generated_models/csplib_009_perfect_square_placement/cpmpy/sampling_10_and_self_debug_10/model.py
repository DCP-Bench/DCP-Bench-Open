
import cpmpy as cp
import json
import numpy as np

# Data
base = 6  # Side length of the large square
sides = [3, 3, 3, 2, 1, 1, 1, 1, 1]  # Side lengths of the smaller squares
n = len(sides)

# Model definition
model = cp.Model()

# Decision Variables: x and y coordinates of the bottom-left corner of each square
# Coordinates must be in range [0, base - side]
x_coords = cp.intvar(0, base, shape=n, name="x_coords")
y_coords = cp.intvar(0, base, shape=n, name="y_coords")

# Constraints
for i in range(n):
    model += x_coords[i] + sides[i] <= base  # squares must fit horizontally in big square
    model += y_coords[i] + sides[i] <= base  # squares must fit vertically in big square

# No overlapping squares
for i in range(n):
    for j in range(i+1, n):
        # Either square i is left of j, or right of j, or below j, or above j
        model += (
            (x_coords[i] + sides[i] <= x_coords[j]) |
            (x_coords[j] + sides[j] <= x_coords[i]) |
            (y_coords[i] + sides[i] <= y_coords[j]) |
            (y_coords[j] + sides[j] <= y_coords[i])
        )

# Objective: none, just find any feasible packing

# Solve and print
if model.solve():
    solution = {
        'x_coords': x_coords.value().tolist(),
        'y_coords': y_coords.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
