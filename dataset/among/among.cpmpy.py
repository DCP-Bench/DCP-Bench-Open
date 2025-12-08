#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/among.py
# Misc: http://www.hakank.org/cpmpy/cpmpy_hakank.py

"""
Requires exactly m values in x to take one of the values in v. All other values may be anything larger than or equal to 0 and less than or equal to 7.

Print the array x (x).
"""

# Data
n = 7  # Length of x
m = 4  # Number of values
v = [1, 5, 6, 7]  # Values to be among in x
# End of data

# Import libraries
from cpmpy import *
import json


def among(m,x,v):
  """
  among(m,x,v)

  Requires exactly m variables in x to take one of the values in v.
  """
  return [m == sum([x[i] == j for i in range(len(x)) for j in v])]


# Decision variables
x = intvar(0, 7, shape=n, name="x")

# Model
model = Model([
    among(m, x, v)
])

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
