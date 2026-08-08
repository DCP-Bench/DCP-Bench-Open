
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

# Decision Variables: bin assignment for each item (0-indexed)
bins = cp.intvar(0, num_bins - 1, shape=n, name="bins")

# Constraints: capacity constraint for each bin
for b in range(num_bins):
    # sum of weights of items assigned to bin b <= capacity
    model += cp.sum([weights[i] * (bins[i] == b) for i in range(n)]) <= capacity

# Solve and print
if model.solve():
    solution = {'bins': bins.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
