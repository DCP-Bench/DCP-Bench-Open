# Import libraries
from cpmpy import *
import json

# Parameters
weights = [4, 3, 1, 3, 2, 5, 2]
capacity = 5
num_bins = 5
n_items = len(weights)

# Decision Variables
bins = intvar(0, num_bins-1, shape=n_items, name="bins")  # Bin assignment for each item

# Model
model = Model()

# Constraint: total weight in each bin does not exceed capacity
for b in range(num_bins):
    model += sum(weights[i] * (bins[i] == b) for i in range(n_items)) <= capacity

# Solve
model.solve()

# Print solution
solution = {
    "bins": bins.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script