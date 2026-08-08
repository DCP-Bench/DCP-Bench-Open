# Data
base = 6  # Side length of the large square
sides = [3, 3, 3, 2, 1, 1, 1, 1, 1]  # Side lengths of the smaller squares
n_squares = len(sides)  # Number of small squares

# Import libraries
from cpmpy import *
import json

# Parameters
max_pos = base  # Maximum coordinate in x or y direction

# Decision variables
x_coords = intvar(0, max_pos - 1, shape=n_squares, name="x_coords")
y_coords = intvar(0, max_pos - 1, shape=n_squares, name="y_coords")

# Model
model = Model()

# Ensure that each square fits within the large square
for i in range(n_squares):
    model += [x_coords[i] + sides[i] <= base]
    model += [y_coords[i] + sides[i] <= base]

# Ensure that no two squares overlap
for i in range(n_squares):
    for j in range(i + 1, n_squares):
        # Square i and j do not overlap if:
        # i is to the right of j
        model += [(x_coords[i] >= x_coords[j] + sides[j]) | 
                  (x_coords[j] >= x_coords[i] + sides[i]) |
                  (y_coords[i] >= y_coords[j] + sides[j]) |
                  (y_coords[j] >= y_coords[i] + sides[i])]

# Solve
model.solve()

# Print the solution
solution = {"x_coords": x_coords.value().tolist(), "y_coords": y_coords.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script