
import cpmpy as cp
import json

# Data (optional)
weights = [4, 3, 1, 3, 2, 5, 2]
capacity = 5
num_bins = 5
n_items = len(weights)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
bins = cp.intvar(0, num_bins-1, shape=n_items, name="bins")

# Constraints
# Capacity constraints: for each bin, the total weight of assigned items <= capacity
for b in range(num_bins):
    model += (cp.sum([weights[i] * (bins[i] == b) for i in range(n_items)]) <= capacity)

# Objective (optional)
# No objective, just find a feasible assignment

# Solve and print
if model.solve():
    solution = {'bins': bins.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
