# Import libraries
from cpmpy import *
import json

# Parameters
base = 6  # Side length of the large square
sides = [3, 3, 3, 2, 1, 1, 1, 1, 1]  # Side lengths of the smaller squares
n_squares = len(sides)

# Decision Variables
x_coords = intvar(0, base, shape=n_squares, name="x_coords")  # x coordinates of squares
y_coords = intvar(0, base, shape=n_squares, name="y_coords")  # y coordinates of squares

# Model
model = Model()

# Constraint: squares must fit within the large square
for i in range(n_squares):
    model += x_coords[i] + sides[i] <= base
    model += y_coords[i] + sides[i] <= base

# Constraint: no two squares overlap
for i in range(n_squares):
    for j in range(i+1, n_squares):
        model += (
            (x_coords[i] + sides[i] <= x_coords[j]) |
            (x_coords[j] + sides[j] <= x_coords[i]) |
            (y_coords[i] + sides[i] <= y_coords[j]) |
            (y_coords[j] + sides[j] <= y_coords[i])
        )

# Solve
model.solve()

# Print solution
solution = {
    "x_coords": x_coords.value().tolist(),
    "y_coords": y_coords.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script