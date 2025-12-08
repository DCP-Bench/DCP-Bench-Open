#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/discrete_tomography.py

"""
This is a little "tomography" problem, taken from an old issue
of Scientific American.

A matrix which contains zeroes and ones gets "x-rayed" vertically and
horizontally, giving the total number of ones in each row and column.
The problem is to reconstruct the contents of the matrix from this
information.

Print the solution matrix with 0 and 1 (matrix) as a list of lists.
"""

# Data
row_sums = [0, 0, 8, 2, 6, 4, 5, 3, 7, 0, 0]  # Each number represents the number of 1s in the row
col_sums = [0, 0, 7, 1, 6, 3, 4, 5, 2, 7, 0, 0]  # Each number represents the number of 1s in the column
# End of data

# Import libraries
from cpmpy import *
import json

r = len(row_sums)
c = len(col_sums)
matrix = intvar(0, 1, shape=(r, c), name="x")

model = Model([
    [sum(row) == row_sums[i] for (row, i) in zip(matrix, range(r))],
    [sum(col) == col_sums[j] for (col, j) in zip(matrix.transpose(), range(c))]
])

# Solve and print the solution
model.solve()

solution = {
    "matrix": matrix.value().tolist()
}
print(json.dumps(solution, indent=4))
# End of CPMPy script
