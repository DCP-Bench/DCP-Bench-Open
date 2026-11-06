#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/coins_grid.py
# Source description: Tony Hurlimann: "A coin puzzle - SVOR-contest 2007" http://www.svor.ch/competitions/competition2007/AsroContestSolution.pdf

# Data
n = 10  # Size of the grid (n x n)
c = 5   # Number of coins in each row and column
# End of data

# Import libraries
from cpmpy import *
import json
import numpy as np


# variables
x = intvar(0, 1, shape=(n, n), name="x")  # The coins on the grid (1 if a coin is placed, 0 otherwise)

model = Model([
    # every row adds up to c
    [sum(row) == c for row in x],

    # every col adds up to c
    [sum(col) == c for col in x.transpose()],
])

# quadratic horizonal distance
z = sum([x[i, j] * abs(i - j) * abs(i - j) for i in range(0, n) for j in range(0, n)])
model.minimize(z)

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist(), "z": z.value()}
print(json.dumps(solution))
# End of CPMPy script
