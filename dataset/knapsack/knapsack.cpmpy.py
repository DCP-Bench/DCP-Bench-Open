#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/knapsack.py

# Data
values = [4, 2, 3, 7, 1]  # Values of the items
weights = [3, 1, 2, 5, 4]  # Weights of the items
capacity = 7  # Capacity of the knapsack
# End of data

# Import libraries
from cpmpy import *
import json

# Construct the model
x = boolvar(shape=len(values), name="x")

model = Model(
    sum(x * weights) <= capacity,
    maximize=sum(x * values)
)

# Solve the model
model.solve()

# Print the solution
solution = {
    "x": x.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script
