#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/bin_packing.py

# Data
weights = [4, 3, 1, 3, 2, 5, 2]
capacity = 5
num_bins = 5
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
n = len(weights)

# Decision variables
bins = intvar(0, num_bins - 1, shape=n, name="bins")  # Which bin each item is assigned to

# Model
model = Model([
    [sum(weights[j] * (bins[j] == i) for j in range(n)) <= capacity for i in range(num_bins)]
])

# Solve the model
model.solve()

# Print the solution
solution = {"bins": bins.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
