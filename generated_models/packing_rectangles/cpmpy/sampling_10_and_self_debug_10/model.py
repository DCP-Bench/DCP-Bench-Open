
import cpmpy as cp
import json
import numpy as np

# Data
widths = [3, 4, 2, 1]
heights = [2, 3, 1, 4]
n = len(widths)

max_width = sum(widths)
max_height = sum(heights)

# Model definition
model = cp.Model()

# Decision Variables
# Position of items (bottom-left corner)
pos_x = cp.intvar(0, max_width, shape=n, name="pos_x")
pos_y = cp.intvar(0, max_height, shape=n, name="pos_y")

# Dimensions of the larger rectangle to minimize area
total_x = cp.intvar(0, max_width, name="total_x")
total_y = cp.intvar(0, max_height, name="total_y")

# Constraints
# Items must be inside the larger rectangle
for i in range(n):
    model += (pos_x[i] + widths[i] <= total_x)
    model += (pos_y[i] + heights[i] <= total_y)

# No overlap constraints between items
for i in range(n):
    for j in range(i+1, n):
        # Item i is to the left or right or above or below item j
        model += (
            (pos_x[i] + widths[i] <= pos_x[j]) |
            (pos_x[j] + widths[j] <= pos_x[i]) |
            (pos_y[i] + heights[i] <= pos_y[j]) |
            (pos_y[j] + heights[j] <= pos_y[i])
        )

# Objective: minimize total area of the larger rectangle
# To linearize the objective, we minimize total_x * total_y by minimizing total_x + total_y as a proxy
# and add a constraint that total_x * total_y <= area, and minimize area.
# But CPMpy does not support multiplication of variables directly in objective.
# Instead, use a binary search approach or minimize total_x + total_y for a heuristic.
# Here, we minimize total_x + total_y as a proxy (encouraging smaller perimeter)
model.minimize(total_x + total_y)

# Solve and print
if model.solve():
    solution = {
        'pos_x': pos_x.value().tolist(),
        'pos_y': pos_y.value().tolist(),
        'total_x': int(total_x.value()),
        'total_y': int(total_y.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
