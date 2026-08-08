
import cpmpy as cp
import json

# Data (optional)
input_data = {
    "roll_width": 10, # The width of the raw rolls
    "widths": [2, 3, 5], # The widths of the smaller pieces to be cut
    "orders": [4, 2, 2], # orders[i] is the number of pieces of width widths[i] needed
    "num_patterns": 2, # The number of available cutting patterns
    "num_rolls_width": [
        [1, 2, 0], # num_rolls_width[i][j] is the number of pieces of width widths[j] in pattern i
        [0, 0, 1]
    ]
}
# End of data

# Extract data
roll_width = input_data["roll_width"]
widths = input_data["widths"]
orders = input_data["orders"]
num_patterns = input_data["num_patterns"]
num_rolls_width = input_data["num_rolls_width"]

# Model definition
model = cp.Model()

# Decision Variables
# Upper bound for number of times a pattern is used: sum of all orders (safe upper bound)
sum_orders = sum(orders)
patterns_used = cp.intvar(0, sum_orders, shape=num_patterns, name="patterns_used")

# Constraints
# For each width j, the total pieces produced across patterns must be >= orders[j]
for j in range(len(widths)):
    model += cp.sum([num_rolls_width[i][j] * patterns_used[i] for i in range(num_patterns)]) >= orders[j]

# Objective: minimize total number of raw rolls used
model.minimize(cp.sum(patterns_used))

# Solve and print
if model.solve():
    solution = {
        'patterns_used': patterns_used.value().tolist(),
        'min_rolls_cut': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
