#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/sudoku.py
# Source description: sudoku.com

"""
The goal of Sudoku is to fill a 9x9 grid with numbers so that each row, column and 3x3 section contain all the digits
between 1 and 9.

Input is a grid with some cells filled with numbers and some empty.

Print the solved grid (grid) as a list of lists.
"""

# Data
input_grid = [  # 0 represents empty cells
    [0, 0, 0,  2, 0, 5,  0, 0, 0],
    [0, 9, 0,  0, 0, 0,  7, 3, 0],
    [0, 0, 2,  0, 0, 9,  0, 6, 0],

    [2, 0, 0,  0, 0, 0,  4, 0, 9],
    [0, 0, 0,  0, 7, 0,  0, 0, 0],
    [6, 0, 9,  0, 0, 0,  0, 0, 1],

    [0, 8, 0,  4, 0, 0,  1, 0, 0],
    [0, 6, 3,  0, 0, 0,  0, 8, 0],
    [0, 0, 0,  6, 0, 8,  0, 0, 0]]
# End of data

# Import libraries
from cpmpy import *
import json
import numpy as np

# Parameters
e = 0  # value for empty cells
given = np.array(input_grid)  # numpy array for easy indexing

# Decision Variables
grid = intvar(1, 9, shape=given.shape, name="grid")

# Model
model = Model(
    # Constraints on given cells (non-empty)
    grid[given != e] == given[given != e],  # numpy's indexing, vectorized equality
    # Constraints on rows and columns
    [AllDifferent(row) for row in grid],
    [AllDifferent(col) for col in grid.T],  # numpy's transpose
)

# Constraints on blocks
for i in range(0, 9, 3):
    for j in range(0, 9, 3):
        model += AllDifferent(grid[i:i+3, j:j+3])  # python's indexing

# Solve
model.solve()

# Print
solution = {"grid": grid.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
