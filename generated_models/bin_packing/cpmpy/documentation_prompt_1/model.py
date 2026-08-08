
import cpmpy as cp
import json

# Data
weights = [4, 3, 1, 3, 2, 5, 2]
capacity = 5
num_bins = 5
num_items = len(weights)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# bins[i] = bin assigned to item i, domain 0..num_bins-1
bins = cp.intvar(0, num_bins-1, shape=num_items, name="bins")

# Constraints
# For each bin, sum of weights of items assigned to it <= capacity
for b in range(num_bins):
    # Create a boolean array indicating if item i is in bin b
    in_bin = [bins[i] == b for i in range(num_items)]
    # sum of weights of items in bin b
    model += cp.sum([weights[i]*in_bin[i] for i in range(num_items)]) <= capacity

# Solve and print
if model.solve():
    solution = {'bins': bins.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
