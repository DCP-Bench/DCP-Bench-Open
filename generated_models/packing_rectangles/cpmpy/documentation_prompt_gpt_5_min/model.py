
import cpmpy as cp
import json

# Data
widths = [3, 4, 2, 1]
heights = [2, 3, 1, 4]
n = len(widths)

# Bounds for the enclosing rectangle
min_total_x = max(widths)
max_total_x = sum(widths)
min_total_y = max(heights)
max_total_y = sum(heights)

# Model definition
model = cp.Model()

# Decision Variables
pos_x = cp.intvar(0, max_total_x, shape=n, name="pos_x")
pos_y = cp.intvar(0, max_total_y, shape=n, name="pos_y")
total_x = cp.intvar(min_total_x, max_total_x, name="total_x")
total_y = cp.intvar(min_total_y, max_total_y, name="total_y")
area = cp.intvar(0, max_total_x * max_total_y, name="area")

# Boolean separation variables: left[i,j] = 1 if item i is strictly left of item j
left = cp.boolvar(shape=(n, n), name="left")
below = cp.boolvar(shape=(n, n), name="below")

# Constraints

# Items must be inside the container
for i in range(n):
    model += pos_x[i] + widths[i] <= total_x
    model += pos_y[i] + heights[i] <= total_y

# No overlap: for every pair i != j, enforce at least one separating relation
for i in range(n):
    # can't be left/below of itself
    model += left[i, i] == 0
    model += below[i, i] == 0
    for j in range(i + 1, n):
        # If left[i,j] then i is left of j (pos_x[i] + w_i <= pos_x[j])
        model += left[i, j].implies(pos_x[i] + widths[i] <= pos_x[j])
        model += left[j, i].implies(pos_x[j] + widths[j] <= pos_x[i])
        # If below[i,j] then i is below j (pos_y[i] + h_i <= pos_y[j])
        model += below[i, j].implies(pos_y[i] + heights[i] <= pos_y[j])
        model += below[j, i].implies(pos_y[j] + heights[j] <= pos_y[i])
        # At least one of left[i,j], left[j,i], below[i,j], below[j,i] must hold
        model += cp.sum([left[i, j], left[j, i], below[i, j], below[j, i]]) >= 1

# Link area = total_x * total_y using a table of all possible products in the domains
table = []
for tx in range(min_total_x, max_total_x + 1):
    for ty in range(min_total_y, max_total_y + 1):
        table.append([tx, ty, tx * ty])
model += cp.Table([total_x, total_y, area], table)

# Objective: minimize area
model.minimize(area)

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
