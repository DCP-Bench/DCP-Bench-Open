#!/usr/bin/python3
# Category: csplib
# Source description: https://www.csplib.org/Problems/prob003/
# Model source: https://www.csplib.org/Problems/prob003/models/QuasiGroup.py.html

# Data
m = 8  # Order of the quasigroup
# End of data

# Import libraries
from cpmpy import *
import json

# Decision Variables
quasigroup = intvar(0, m - 1, shape=(m, m), name="quasigroup")

# Model
model = Model()

# Each element occurs once in every row
for i in range(m):
    model += AllDifferent(quasigroup[i, :])

# Each element occurs once in every column
for j in range(m):
    model += AllDifferent(quasigroup[:, j])

# QG3.m property: (a*b)*(b*a) = a
for a in range(m):
    for b in range(m):
        model += quasigroup[quasigroup[a, b], quasigroup[b, a]] == a


# Solve
model.solve()

# Print
solution = {"quasigroup": quasigroup.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
