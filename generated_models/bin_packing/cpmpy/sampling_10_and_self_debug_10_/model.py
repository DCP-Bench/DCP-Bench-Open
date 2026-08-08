
import cpmpy as cp
import json

# Data
weights = [4, 3, 1, 3, 2, 5, 2]
capacity = 5
num_bins = 5
n = len(weights)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
bins = cp.intvar(0, num_bins - 1, shape=n, name="bins")  # bin index for each item (0-indexed)

# Constraints
# For each bin, the total weight of items assigned to that bin must not exceed capacity
for b in range(num_bins):
    model += cp.sum([weights[i] * (bins[i] == b) for i in range(n)]) <= capacity

# Solve and print
if model.solve():
    solution = {'bins': bins.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
