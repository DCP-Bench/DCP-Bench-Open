
import cpmpy as cp
import json

# Data
weights = [4, 3, 1, 3, 2, 5, 2]
capacity = 5
num_bins = 5

# Model definition
model = cp.Model()

# Decision Variables
n_items = len(weights)
bins = cp.intvar(0, num_bins - 1, shape=n_items, name="bins")

# Constraints
for i in range(num_bins):
    # Sum of weights in bin i must be <= capacity
    total = cp.sum(weights[j] * (bins[j] == i) for j in range(n_items))
    model += (total <= capacity)

# Solve and print
if model.solve():
    solution = {'bins': bins.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
