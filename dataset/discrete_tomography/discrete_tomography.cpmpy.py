#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/discrete_tomography.py

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
