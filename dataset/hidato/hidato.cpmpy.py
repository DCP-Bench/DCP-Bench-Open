#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/hidato.py

"""
Hidato Puzzles start semi-filled with numbered tiles.
Connect the numbers together to win. Consecutive
number must touch horizontally, vertically, or
diagonally. The numbers must be in increasing order.
Fill in the empty cells with the numbers that
complete the puzzle.

Print the solved puzzle (x) as a list of lists of integers.
"""

# Data
# 0 is for empty cells that need to be filled. 1-144 are the numbers that are already filled.
puzzle = [[0, 0, 134, 2, 4, 0, 0, 0, 0, 0, 0, 0],
          [136, 0, 0, 1, 0, 5, 6, 10, 115, 106, 0, 0],
          [139, 0, 0, 124, 0, 122, 117, 0, 0, 107, 0, 0],
          [0, 131, 126, 0, 123, 0, 0, 12, 0, 0, 0, 103],
          [0, 0, 144, 0, 0, 0, 0, 0, 14, 0, 99, 101],
          [0, 0, 129, 0, 23, 21, 0, 16, 65, 97, 96, 0],
          [30, 29, 25, 0, 0, 19, 0, 0, 0, 66, 94, 0],
          [32, 0, 0, 27, 57, 59, 60, 0, 0, 0, 0, 92],
          [0, 40, 42, 0, 56, 58, 0, 0, 72, 0, 0, 0],
          [0, 39, 0, 0, 0, 0, 78, 73, 71, 85, 69, 0],
          [35, 0, 0, 46, 53, 0, 0, 0, 80, 84, 0, 0],
          [36, 0, 45, 0, 0, 52, 51, 0, 0, 0, 0, 88]]
# End of data

# Import libraries
from cpmpy import *
import numpy as np
import json
import math

model = Model()

r, c = len(puzzle), len(puzzle[0])

x = intvar(1, r * c, shape=(c, r), name="x")

model += AllDifferent(x)

# Fill in the known values
for i in range(r):
    for j in range(c):
        if puzzle[i][j] > 0:
            model += [x[i, j] == puzzle[i][j]]

# From the numbers k = 1 to r*c-1, find this position, and then the position of k+1
for k in range(1, r * c):
    i = intvar(0, r)
    j = intvar(0, c)
    a = intvar(-1, 1)
    b = intvar(-1, 1)

    # 1) First: fix "this" k
    # 2) and then find the position of the next value (k+1)
    model += [
        k == x[i,j],
        k + 1 == x[i+a,j+b]
    ]

    # Ensure that the next value is within the matrix, and that it is not the same cell
    model += [
        i + a >= 0,
        j + b >= 0,
        i + a < r,
        j + b < c,
        ((a != 0) | (b != 0))
    ]

# Solve
model.solve()

# Output
solution = {
    "x": x.value().tolist(),
}
print(json.dumps(solution))
# End of CPMPy script
