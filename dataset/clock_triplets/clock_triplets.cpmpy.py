#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/clock_triplets.py
# Source description: http://www.f1compiler.com/samples/Dean%20Clark%27s%20Problem.f1.html

"""
Rearrange the numbers on the face of a clock (1 to 12) so no triplet of adjacent numbers has a sum higher than 21.
This is the smallest value that the highest sum of a triplet can have.

Print the arrangement of the numbers on the clock (x) as a list of 12 integers - ranging from 1 to 12.
"""

# Import libraries
from cpmpy import *
import json

# Parameters
n = 12

# variables
x = intvar(1, n, shape=n, name="x")  # The numbers on the clock
triplet_sum = intvar(0, 21, name="triplet_sum")

# constraints
model = Model([AllDifferent(x),
               # <SYMMETRY_BREAKING_CONSTRAINT_START>
               # x[1] > x[11],
               # <SYMMETRY_BREAKING_CONSTRAINT_END>
               [(x[i % 12] + x[(i % 12) - 1] + x[(i % 12) - 2]) <= triplet_sum for i in range(n)],
               ])

# Solve
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
