
import cpmpy as cp
import json

# Input data
widths = [3, 4, 2, 1]
heights = [2, 3, 1, 4]
N = len(widths)
sum_width = sum(widths)
sum_height = sum(heights)

# Variables
pos_x = cp.intvar(0, sum_width, shape=N, name="pos_x")
pos_y = cp.intvar(0, sum_height, shape=N, name="pos_y")
total_x = cp.intvar(1, sum_width, name="total_x")
total_y = cp.intvar(1, sum_height, name="total_y")

model = cp.Model()

# Constraints for item positions within total dimensions
for i in range(N):
    model += (pos_x[i] + widths[i] <= total_x)
    model += (pos_y[i] + heights[i] <= total_y)

# Non-overlapping constraints between all pairs of items
for i in range(N):
    for j in range(i + 1, N):
        cond1 = (pos_x[i] + widths[i] <= pos_x[j])
        cond2 = (pos_x[j] + widths[j] <= pos_x[i])
        cond3 = (pos_y[i] + heights[i] <= pos_y[j])
        cond4 = (pos_y[j] + heights[j] <= pos_y[i])
        model += (cond1 | cond2 | cond3 | cond4)

# Objective: minimize total area
model.minimize(total_x * total_y)

# Solve and print solution
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
