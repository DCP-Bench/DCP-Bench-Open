#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/18_hole_golf.py

"""
Generate a random 18-hole golf course where each hole has a length of 3, 4, or 5, and the total length of the course is 72.

Print the lengths of the holes (holes) as a list of 18 integers.
"""

# Import libraries
from cpmpy import *
import json

# Parameters
num_holes = 18  # Number of holes
total_length = 72  # Total length of the course
hole_lengths = [3, 4, 5]  # Possible lengths for each hole

# Decision variables
holes = intvar(3, 5, shape=num_holes, name="holes")  # Lengths of the holes

# Model
model = Model([
    sum(holes) == total_length
])

# Solve the model
model.solve()

# Print the solution
solution = {"holes": holes.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
