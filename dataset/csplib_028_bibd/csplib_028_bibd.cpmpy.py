#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob028_bibd.py
# Source description: https://www.csplib.org/Problems/prob028/

# Data
v = 9  # Number of distinct objects
b = 12  # Number of blocks
r = 4  # Number of blocks each object occurs in
k = 3  # Number of objects each block contains
l = 1  # Number of blocks in which each pair of distinct objects occurs together
# End of data

# Import libraries
import json
import numpy as np
from cpmpy import *
from cpmpy.expressions.utils import all_pairs

def bibd(v, b, r, k, l):
    matrix = boolvar(shape=(v, b), name="matrix")

    model = Model()

    # Every row adds up to r
    model += [sum(row) == r for row in matrix]
    # Every column adds up to k
    model += [sum(col) == k for col in matrix.T]

    # The scalar product of every pair of columns adds up to l
    model += [np.dot(row_i, row_j) == l for row_i, row_j in all_pairs(matrix)]

    return model, (matrix,)

# Example usage
model, (matrix,) = bibd(v, b, r, k, l)
model.solve()

# Print
solution = {"matrix": matrix.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script

