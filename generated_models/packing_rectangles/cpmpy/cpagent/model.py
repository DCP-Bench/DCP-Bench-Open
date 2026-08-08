import cpmpy as cp
import numpy as np
import json
from itertools import combinations

# Step 1: Input data and problem analysis
widths = [3, 4, 2, 1]
heights = [2, 3, 1, 4]
n_items = len(widths)

# Upper bounds for container dimensions
max_total_x = sum(widths)
max_total_y = sum(heights)

# Step 2: Decision variables
# Position of each item (bottom-left corner)
pos_x = cp.intvar(0, max_total_x, shape=n_items, name="pos_x")
pos_y = cp.intvar(0, max_total_y, shape=n_items, name="pos_y")

# Container dimensions
total_x = cp.intvar(1, max_total_x, name="total_x")
total_y = cp.intvar(1, max_total_y, name="total_y")

model = cp.Model()

# Step 3: Constraints

# 1. Boundary constraints: items must fit within the container
for i in range(n_items):
    model += pos_x[i] + widths[i] <= total_x
    model += pos_y[i] + heights[i] <= total_y

# 2. Non-overlap constraints
# For each pair of items, they must not overlap
for i, j in combinations(range(n_items), 2):
    model += (
        (pos_x[i] + widths[i] <= pos_x[j]) |  # i left of j
        (pos_x[j] + widths[j] <= pos_x[i]) |  # j left of i
        (pos_y[i] + heights[i] <= pos_y[j]) |  # i below j
        (pos_y[j] + heights[j] <= pos_y[i])    # j below i
    )

# 3. Symmetry breaking: fix the first item at origin
model += pos_x[0] == 0
model += pos_y[0] == 0

# Step 4: Optimization objective
total_area = total_x * total_y
model.minimize(total_area)

# Step 5: Solve and output
if model.solve():
    # Extract solution values
    pos_x_vals = pos_x.value()
    pos_y_vals = pos_y.value()
    total_x_val = total_x.value()
    total_y_val = total_y.value()
    
    # Create solution in required format
    solution = {
        "pos_x": pos_x_vals.tolist() if hasattr(pos_x_vals, 'tolist') else list(pos_x_vals),
        "pos_y": pos_y_vals.tolist() if hasattr(pos_y_vals, 'tolist') else list(pos_y_vals),
        "total_x": int(total_x_val),
        "total_y": int(total_y_val)
    }
    
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))