
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
# coordinates start from 0, and must fit within the big square
x = cp.intvar(0, base, shape=n, name="x")
y = cp.intvar(0, base, shape=n, name="y")

# Constraints: each square must be fully inside the big square
for i in range(n):
    model += x[i] + sides[i] <= base
    model += y[i] + sides[i] <= base

# Non-overlap constraints: for each pair of squares, at least one separating relation holds
for i in range(n):
    for j in range(i + 1, n):
        model += cp.Or(
            x[i] + sides[i] <= x[j],  # i is to the left of j
            x[j] + sides[j] <= x[i],  # j is to the left of i
            y[i] + sides[i] <= y[j],  # i is below j
            y[j] + sides[j] <= y[i]   # j is below i
        )

# (Optional) The instance is a perfect packing by area; no additional area constraint needed.

# Solve and print
if model.solve():
    solution = {
        'x_coords': x.value().tolist(),
        'y_coords': y.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
