#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/futoshiki.py

"""
The futoshiki puzzle is played on a square grid, such as 5 x 5. The objective
is to place the numbers 1 to 5 (or whatever the dimensions are)
such that each row, and column contains each of the digits 1 to 5.
Some digits may be given at the start. In addition, inequality
constraints are also initially specified between some of the squares,
such that one must be higher or lower than its neighbour. These
constraints must be honoured as the grid is filled out.

Print the completed grid (grid) that satisfies the above conditions as a list of lists of integers.
"""

# Data
# values[i,j] is the value in row i, column j. 0 means not set.
values = [[0, 0, 3, 2, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0]]

# [i1,j1, i2,j2] requires that values[i1,j1] < values[i2,j2]
# Note: 1-based
lt = [[1, 2, 1, 1], [1, 4, 1, 5], [2, 3, 1, 3], [3, 3, 2, 3], [3, 4, 2, 4],
       [2, 5, 3, 5], [3, 2, 4, 2], [4, 4, 4, 3], [5, 2, 5, 1], [5, 4, 5, 3],
       [5, 5, 4, 5]]
# End of data

# Import libraries
from cpmpy import *
import numpy as np
import json

size = len(values)
RANGE = list(range(size))
NUMQD = list(range(len(lt)))

# variables
grid = intvar(1, size, shape=(size, size), name="field")

# constraints
model = Model()

# set initial values
for row in RANGE:
    for col in RANGE:
        if values[row][col] > 0:
            model += [grid[row, col] == values[row][col]]

# all rows have to be different
for row in RANGE:
    model += [AllDifferent([grid[row, col] for col in RANGE])]

# all columns have to be different
for col in RANGE:
    model += [AllDifferent([grid[row, col] for row in RANGE])]

# all < constraints are satisfied
# Also: make 0-based
for i in NUMQD:
    model += [grid[lt[i][0] - 1, lt[i][1] - 1] < grid[lt[i][2] - 1, lt[i][3] - 1]]

# Solve
model.solve()

# Output
solution = {
    "grid": grid.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script
