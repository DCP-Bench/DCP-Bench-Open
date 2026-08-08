
import cpmpy as cp
import json

# Data
base = 6  # Side length of the large square
sides = [3, 3, 3, 2, 1, 1, 1, 1, 1]  # Side lengths of the smaller squares
n = len(sides)

# Model definition
model = cp.Model()

# Decision Variables
# x_coords and y_coords are the coordinates of the bottom-left corner of each square
x_coords = cp.intvar(0, base, shape=n, name="x_coords")
y_coords = cp.intvar(0, base, shape=n, name="y_coords")

# Constraints
for i in range(n):
    # Each square must be inside the big square
    model += (x_coords[i] + sides[i] <= base)
    model += (y_coords[i] + sides[i] <= base)

# No overlap constraints
for i in range(n):
    for j in range(i+1, n):
        # Squares i and j do not overlap:
        # Either i is to the left of j, or i is to the right of j,
        # or i is above j, or i is below j
        model += (
            (x_coords[i] + sides[i] <= x_coords[j]) |
            (x_coords[j] + sides[j] <= x_coords[i]) |
            (y_coords[i] + sides[i] <= y_coords[j]) |
            (y_coords[j] + sides[j] <= y_coords[i])
        )

# Solve and print
if model.solve():
    solution = {
        'x_coords': x_coords.value().tolist(),
        'y_coords': y_coords.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
