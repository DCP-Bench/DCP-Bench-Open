#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/giant_cat_army_riddle.py

# Import libraries
from cpmpy import *
import numpy as np
import json

maxval = 60
n = 24

# variables
x = intvar(0, maxval, shape=n, name="x")

model = Model([AllDifferent(x)])

# Given
model += [x[0] == 0]

# x[1] == 5 || x[1] == 7
model += [(x[1] == 5) | (x[1] == 7)]
model += (x[n - 1] == 14)

for i in range(n - 1):
    model += [(x[i + 1] == x[i] + 5) |
              (x[i + 1] == x[i] + 7) |
              (x[i] == x[i + 1] * x[i + 1])]

# 0 .. 2 .. 10 .. 14
ix2 = intvar(1, n, name="ix2")
ix10 = intvar(1, n, name="ix10")
model += [2 == x[ix2]]
model += [10 == x[ix10]]
model += [ix2 < ix10]

# Solve
model.solve()

# Output
solution = {
    "x": x.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script
