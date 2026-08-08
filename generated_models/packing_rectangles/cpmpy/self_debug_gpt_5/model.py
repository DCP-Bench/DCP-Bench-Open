
import cpmpy as cp
import json

# Data (optional)
widths = [3, 4, 2, 1]  # Widths of the items
heights = [2, 3, 1, 4]  # Heights of the items
# End of data

n = len(widths)
sum_w = int(sum(widths))
sum_h = int(sum(heights))
max_w = int(max(widths))
max_h = int(max(heights))

# Model definition
model = cp.Model()

# Decision Variables
# Positions (starting from 0)
pos_x = [cp.intvar(0, sum_w - widths[i], name=f"pos_x_{i}") for i in range(n)]
pos_y = [cp.intvar(0, sum_h - heights[i], name=f"pos_y_{i}") for i in range(n)]

# Dimensions of the larger rectangle
total_x = cp.intvar(max_w, sum_w, name="total_x")
total_y = cp.intvar(max_h, sum_h, name="total_y")

# Area variable to minimize (we will link it to total_x * total_y via a table)
area = cp.intvar(0, sum_w * sum_h, name="area")

# Constraints

# Each item must be within the bounds of the larger rectangle
for i in range(n):
    model += (pos_x[i] + widths[i] <= total_x)
    model += (pos_y[i] + heights[i] <= total_y)

# Non-overlapping constraints: for every pair of rectangles, at least one separation holds
for i in range(n):
    for j in range(i + 1, n):
        model += (
            (pos_x[i] + widths[i] <= pos_x[j]) |  # i is left of j
            (pos_x[j] + widths[j] <= pos_x[i]) |  # j is left of i
            (pos_y[i] + heights[i] <= pos_y[j]) | # i is below j
            (pos_y[j] + heights[j] <= pos_y[i])   # j is below i
        )

# Link area = total_x * total_y using a Table of allowed combinations
table = []
for X in range(max_w, sum_w + 1):
    for Y in range(max_h, sum_h + 1):
        table.append([X, Y, X * Y])
model += cp.Table([total_x, total_y, area], table)

# Objective (minimize total area)
model.minimize(area)

# Solve and print
if model.solve():
    solution = {
        'pos_x': [int(v.value()) for v in pos_x],
        'pos_y': [int(v.value()) for v in pos_y],
        'total_x': int(total_x.value()),
        'total_y': int(total_y.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
