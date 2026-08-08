from cpmpy import *
import json

# Parameters
widths = [3, 4, 2, 1]  # Widths of the items
heights = [2, 3, 1, 4]  # Heights of the items
n_items = len(widths)

# Decision Variables
max_total = sum(widths) * sum(heights)  # Upper bound for total area
total_x = intvar(1, max_total, name="total_x")  # Width of the larger rectangle
total_y = intvar(1, max_total, name="total_y")  # Height of the larger rectangle
pos_x = intvar(0, max_total, shape=n_items, name="pos_x")  # x positions of items
pos_y = intvar(0, max_total, shape=n_items, name="pos_y")  # y positions of items

# Model
model = Model()

# Constraint: all items must fit within the larger rectangle
for i in range(n_items):
    model += pos_x[i] + widths[i] <= total_x
    model += pos_y[i] + heights[i] <= total_y

# Constraint: no overlapping items
for i in range(n_items):
    for j in range(i+1, n_items):
        # Item i is left, right, below or above item j
        model += (pos_x[i] + widths[i] <= pos_x[j]) | \
                 (pos_x[j] + widths[j] <= pos_x[i]) | \
                 (pos_y[i] + heights[i] <= pos_y[j]) | \
                 (pos_y[j] + heights[j] <= pos_y[i])

# Objective: minimize total area
model.minimize(total_x * total_y)

# Solve
model.solve()

# Print solution
solution = {
    "pos_x": pos_x.value().tolist(),
    "pos_y": pos_y.value().tolist(),
    "total_x": total_x.value(),
    "total_y": total_y.value()
}
print(json.dumps(solution))
# End of CPMPy script