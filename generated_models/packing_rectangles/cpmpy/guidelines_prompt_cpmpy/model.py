
import cpmpy as cp
import json

# Data
widths = [3, 4, 2, 1]   # Widths of the items
heights = [2, 3, 1, 4]  # Heights of the items
n = len(widths)
sum_w = sum(widths)
sum_h = sum(heights)
max_w = max(widths)
max_h = max(heights)

# Model definition
model = cp.Model()

# Decision Variables
pos_x = cp.intvar(0, sum_w, shape=n, name="pos_x")
pos_y = cp.intvar(0, sum_h, shape=n, name="pos_y")
total_x = cp.intvar(max_w, sum_w, name="total_x")
total_y = cp.intvar(max_h, sum_h, name="total_y")
area = cp.intvar(0, sum_w * sum_h, name="area")

# Constraints

# 1) Each item must be inside the bigger rectangle
for i in range(n):
    model += [
        pos_x[i] + widths[i] <= total_x,
        pos_y[i] + heights[i] <= total_y
    ]

# 2) Non-overlap constraints using disjunctive boolean variables
#    For each pair i<j, we enforce one of: i left of j, i right of j,
#    i below j, or i above j.
M_x = sum_w
M_y = sum_h
for i in range(n):
    for j in range(i + 1, n):
        left_ij  = cp.boolvar(name=f"left_{i}_{j}")
        right_ij = cp.boolvar(name=f"right_{i}_{j}")
        below_ij = cp.boolvar(name=f"below_{i}_{j}")
        above_ij = cp.boolvar(name=f"above_{i}_{j}")
        # Exactly one positional relation holds
        model += left_ij + right_ij + below_ij + above_ij == 1
        # If left_ij = 1 then pos_x[i] + w_i <= pos_x[j], else relaxed by M_x
        model += pos_x[i] + widths[i] <= pos_x[j] + M_x * (1 - left_ij)
        # If right_ij = 1 then pos_x[j] + w_j <= pos_x[i]
        model += pos_x[j] + widths[j] <= pos_x[i] + M_x * (1 - right_ij)
        # If below_ij = 1 then pos_y[i] + h_i <= pos_y[j]
        model += pos_y[i] + heights[i] <= pos_y[j] + M_y * (1 - below_ij)
        # If above_ij = 1 then pos_y[j] + h_j <= pos_y[i]
        model += pos_y[j] + heights[j] <= pos_y[i] + M_y * (1 - above_ij)

# 3) Link area = total_x * total_y via an allowed‐assignments table
#    Because CPMpy doesn't directly support nonlinear objectives, we
#    enumerate all (x, y, x*y) tuples and restrict (total_x, total_y, area)
table = []
for x_val in range(max_w, sum_w + 1):
    for y_val in range(max_h, sum_h + 1):
        table.append([x_val, y_val, x_val * y_val])
model += cp.allowedAssignments([total_x, total_y, area], table)

# Objective: minimize the packed area
model.minimize(area)

# Solve and print
if model.solve():
    solution = {
        "pos_x": pos_x.value().tolist(),
        "pos_y": pos_y.value().tolist(),
        "total_x": int(total_x.value()),
        "total_y": int(total_y.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
