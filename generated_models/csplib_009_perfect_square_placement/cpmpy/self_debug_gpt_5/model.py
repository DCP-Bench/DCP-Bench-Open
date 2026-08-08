
import cpmpy as cp
import json

# Data
base = 6  # Side length of the large square
sides = [3, 3, 3, 2, 1, 1, 1, 1, 1]  # Side lengths of the smaller squares
n = len(sides)

# Model definition
model = cp.Model()

# Decision Variables
# x[i], y[i] are the bottom-left integer coordinates of square i
x_coords = [cp.intvar(0, base - sides[i], name=f"x_{i}") for i in range(n)]
y_coords = [cp.intvar(0, base - sides[i], name=f"y_{i}") for i in range(n)]

# Constraints
# Non-overlapping: for all pairs i<j, one of the disjunctive separation conditions must hold
for i in range(n):
    for j in range(i + 1, n):
        si = sides[i]
        sj = sides[j]
        model += (
            (x_coords[i] + si <= x_coords[j]) |
            (x_coords[j] + sj <= x_coords[i]) |
            (y_coords[i] + si <= y_coords[j]) |
            (y_coords[j] + sj <= y_coords[i])
        )

# Symmetry breaking for identical sizes: enforce lexicographic order on (x,y)
for i in range(n):
    for j in range(i + 1, n):
        if sides[i] == sides[j]:
            model += (x_coords[i] < x_coords[j]) | ((x_coords[i] == x_coords[j]) & (y_coords[i] <= y_coords[j]))

# Solve and print
if model.solve():
    solution = {
        'x_coords': [int(v.value()) for v in x_coords],
        'y_coords': [int(v.value()) for v in y_coords]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
