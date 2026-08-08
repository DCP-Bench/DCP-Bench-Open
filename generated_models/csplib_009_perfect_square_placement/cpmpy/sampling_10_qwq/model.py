
import cpmpy as cp
import json

base = 6
sides = [3, 3, 3, 2, 1, 1, 1, 1, 1]

# Decision variables for x and y coordinates of each square
x = []
y = []
for i, s in enumerate(sides):
    max_coord = base - s
    x.append(cp.intvar(0, max_coord, name=f"x_{i}"))
    y.append(cp.intvar(0, max_coord, name=f"y_{i}"))

model = cp.Model()

# Non-overlapping constraints between all pairs of squares
for i in range(len(sides)):
    for j in range(i + 1, len(sides)):
        s_i, s_j = sides[i], sides[j]
        # Conditions to prevent overlap in x or y direction
        cond_x1 = (x[i] + s_i <= x[j])
        cond_x2 = (x[j] + s_j <= x[i])
        cond_y1 = (y[i] + s_i <= y[j])
        cond_y2 = (y[j] + s_j <= y[i])
        model += (cond_x1 | cond_x2 | cond_y1 | cond_y2)

# Solve the model
if model.solve():
    x_coords = [int(var.value()) for var in x]
    y_coords = [int(var.value()) for var in y]
    solution = {
        'x_coords': x_coords,
        'y_coords': y_coords
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
