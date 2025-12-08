#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/added_corner.py

"""
Enter the digits 1 through 8 in the circles and squares such that the number in each square is equal to the sum of the numbers in the adjoining circles.
...
  C F C
  F   F
  C F C
'''

Print the values for each position (positions), starting from the top left corner and moving like reading a book, i.e., left to right, top to bottom.
"""

# Import libraries
from cpmpy import *
import json

# Parameters
n = 8  # Number of digits

# Decision variables
positions = intvar(1, n, shape=n, name="positions")
a, b, c, d, e, f, g, h = positions

# Model
model = Model([
    AllDifferent(positions),
    b == a + c,
    d == a + f,
    e == c + h,
    g == f + h
])

# Solve the model
model.solve()

# Print the solution
solution = {"positions": positions.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
