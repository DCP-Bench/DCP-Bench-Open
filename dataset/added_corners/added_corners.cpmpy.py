#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/added_corner.py

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
