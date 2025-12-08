#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/3sum.py

"""
Given a collection of integers, find a number of elements that sum to zero.

Print whether each element is selected (indices) as a list of booleans.
"""

# Data
nums = [-1, 6, 8, 9, 10, -100, 78, 0, 1]  # Collection of integers
m = 3  # The number of elements that should sum to 0
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
n = len(nums)

# Decision variables
indices = boolvar(shape=n, name="indices")  # Boolean array to indicate which elements are selected

# Model
model = Model([
    sum([nums[i] * indices[i] for i in range(n)]) == 0,
    sum(indices) == m
])

# Solve the model
model.solve()

# Print the solution
solution = {"indices": indices.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script