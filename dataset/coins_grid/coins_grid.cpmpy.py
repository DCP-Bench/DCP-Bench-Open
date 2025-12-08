#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/coins_grid.py
# Source description: Tony Hurlimann: "A coin puzzle - SVOR-contest 2007" http://www.svor.ch/competitions/competition2007/AsroContestSolution.pdf

"""
In a quadratic grid (or a larger chessboard) n by n, one should
 place coins in such a way that the following conditions are fulfilled:
   1. In each row exactly c coins must be placed.
   2. In each column exactly c coins must be placed.
   3. The sum of the quadratic horizontal distance from the main
      diagonal of all cells containing a coin must be as
      small as possible.
   4. In each cell at most one coin can be placed.

Print whether a coin is placed in each cell (x) as a list of lists of booleans, and the sum of the quadratic horizontal
distance from the main diagonal (z) as an integer.
"""

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
