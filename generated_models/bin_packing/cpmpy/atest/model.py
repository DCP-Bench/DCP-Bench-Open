from cpmpy import *
import json

# Input data
weights = [4, 3, 1, 3, 2, 5, 2]
capacity = 5
num_bins = 5

# Number of items
num_items = len(weights)

# Decision variables
# bins[i] = j means item i is assigned to bin j
bins = intvar(0, num_bins - 1, shape=num_items, name="bins")

# Model
model = Model()

# Each bin's total weight must not exceed the capacity
for b in range(num_bins):
    # Use CPMPy's element and sum to express the constraint
    model += [sum([weights[i] * (bins[i] == b) for i in range(num_items)]) <= capacity]

# Solve the model
model.solve()

# Print the solution
solution = {"bins": bins.value().tolist()}
print(json.dumps(solution))