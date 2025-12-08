#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/bin_packing.py

"""
Given several items of specific weights and a number of bins of a fixed capacity, assign each item to a bin so that the total weight of the items in each bin does not exceed the capacity.

Print the bin each item is assigned to (bins) as a list of numbers, 0-indexed.
"""

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
    [sum(weights[j] * (bins[j] == i) for j in range(n)) <= capacity for i in range(n)]
])

# Solve the model
model.solve()

# Print the solution
solution = {"bins": bins.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
