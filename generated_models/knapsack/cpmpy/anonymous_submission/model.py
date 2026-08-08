# Import libraries
from cpmpy import *
import json

# Parameters
values = [4, 2, 3, 7, 1]  # Values of the items
weights = [3, 1, 2, 5, 4]  # Weights of the items
capacity = 7  # Capacity of the knapsack
n_items = len(values)

# Decision Variables
x = boolvar(shape=n_items, name="x")  # Whether to take each item (1) or not (0)

# Model
model = Model()

# Constraint: total weight does not exceed capacity
model += sum(weights[i] * x[i] for i in range(n_items)) <= capacity

# Objective: maximize total value
model.maximize(sum(values[i] * x[i] for i in range(n_items)))

# Solve
model.solve()

# Print solution
solution = {
    "x": x.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script