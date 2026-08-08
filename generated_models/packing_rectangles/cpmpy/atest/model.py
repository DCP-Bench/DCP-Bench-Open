from cpmpy import *
import json

# Input data
widths = [3, 4, 2, 1]  # Widths of the items
heights = [2, 3, 1, 4]  # Heights of the items
num_items = len(widths)

# Decision variables
# pos_x[i] and pos_y[i] are the x and y coordinates of the bottom-left corner of item i
pos_x = intvar(0, 100, shape=num_items, name="pos_x")
pos_y = intvar(0, 100, shape=num_items, name="pos_y")

# total_x and total_y are the dimensions of the larger rectangle
total_x = intvar(0, 100, name="total_x")
total_y = intvar(0, 100, name="total_y")

# Model
model = Model()

# Objective: minimize the total area of the larger rectangle
model.minimize(total_x * total_y)

# Constraints to ensure each item fits within the larger rectangle
for i in range(num_items):
    model += [pos_x[i] + widths[i] <= total_x]
    model += [pos_y[i] + heights[i] <= total_y]

# Constraints to ensure no overlap between items
for i in range(num_items):
    for j in range(i + 1, num_items):
        # Either the rectangles are separated in x or y direction
        model += (pos_x[i] + widths[i] <= pos_x[j]) | (pos_x[j] + widths[j] <= pos_x[i]) | \
                 (pos_y[i] + heights[i] <= pos_y[j]) | (pos_y[j] + heights[j] <= pos_y[i])

# Solve the model
model.solve()

# Print the solution
solution = {
    "pos_x": pos_x.value().tolist(),
    "pos_y": pos_y.value().tolist(),
    "total_x": total_x.value(),
    "total_y": total_y.value()
}
print(json.dumps(solution))