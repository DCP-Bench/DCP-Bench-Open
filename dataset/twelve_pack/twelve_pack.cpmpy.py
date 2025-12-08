#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/12_pack_problem.py

"""
Given a target number of items, find the closest combination of packs of different sizes that meets or exceeds the target.

Print the counts of each pack size used (counts) as a list of integers.
"""

# Data
target = 94  # Target number of items
packs = [7, 13]  # Pack sizes
# End of data

# Import libraries
from cpmpy import *
import json
import builtins

# Parameters
n = len(packs)
max_val = target * 2  # Arbitrary max limit of pack counts

# Decision variables
counts = intvar(0, max_val, shape=n, name="counts")  # Count of each pack size used
total = intvar(0, max_val * n, name="total")  # Total number of items

# Model
model = Model([
    total == (counts * packs).sum(),
    total >= target,
])

# Objective
model.minimize(total)

# Solve the model
model.solve()

# Print the solution
solution = {"counts": counts.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script