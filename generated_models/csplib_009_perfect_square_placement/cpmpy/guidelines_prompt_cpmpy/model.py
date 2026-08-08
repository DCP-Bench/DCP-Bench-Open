
import cpmpy as cp
import json

# Data
base = 6  # Side length of the large square
sides = [3, 3, 3, 2, 1, 1, 1, 1, 1]  # Side lengths of the smaller squares
n = len(sides)
# End of data

# Model definition
model = cp.Model()

# Decision Variables: bottom-left coordinates of each small square
x = [cp.intvar(0, base - sides[i], name=f"x{i}") for i in range(n)]
y = [cp.intvar(0, base - sides[i], name=f"y{i}") for i in range(n)]

# Constraints: no overlap between any two squares
for i in range(n):
    for j in range(i + 1, n):
        si, sj = sides[i], sides[j]
        model += [
            (x[i] + si <= x[j])
            | (x[j] + sj <= x[i])
            | (y[i] + si <= y[j])
            | (y[j] + sj <= y[i])
        ]

# All squares must lie within the big square (already enforced by variable domains)

# Solve and print
if model.solve():
    x_coords = [int(v.value()) for v in x]
    y_coords = [int(v.value()) for v in y]
    solution = {
        "x_coords": x_coords,
        "y_coords": y_coords
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
