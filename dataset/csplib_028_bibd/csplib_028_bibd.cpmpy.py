#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob028_bibd.py
# Source description: https://www.csplib.org/Problems/prob028/

"""
Balanced Incomplete Block Design (BIBD) generation is a standard combinatorial problem from design theory, originally
used in the design of statistical experiments but since finding other applications such as cryptography. It is a
special case of Block Design, which also includes Latin Square problems.

A BIBD is defined as an arrangement of \( v \) distinct objects into \( b \) blocks such that each block contains exactly \( k \) distinct objects, each object occurs
in exactly \( r \) different blocks, and every two distinct objects occur together in exactly \( \lambda \) blocks.
Another way of defining a BIBD is in terms of its incidence matrix, which is a \( v \) by \( b \) binary matrix with
exactly \( r \) ones per row, \( k \) ones per column, and with a scalar product of \( \lambda \) between any pair of
distinct rows. A BIBD is therefore specified by its parameters \( (v, b, r, k, \lambda) \). An example of a solution
for \( (7, 7, 3, 3, 1) \) is:

0 1 1 0 0 1 0
1 0 1 0 1 0 0
0 0 1 1 0 0 1
1 1 0 0 0 0 1
0 0 0 0 1 1 1
1 0 0 1 0 1 0
0 1 0 1 1 0 0

Print the incidence matrix of the BIBD (matrix) as a list of lists of integers - 0s and 1s.
"""

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

    # Break symmetry
    # <SYMMETRY_BREAKING_CONSTRAINT_START>
    # # Lexicographic ordering of rows
    # for r in range(v - 1):
    #     bvar = boolvar(shape=(b + 1))
    #     model += bvar[0] == 1
    #     model += bvar == ((matrix[r] <= matrix[r + 1]) &
    #                       ((matrix[r] < matrix[r + 1]) | (bvar[1:] == 1)))
    #     model += bvar[-1] == 0
    # # Lexicographic ordering of columns
    # for c in range(b - 1):
    #     bvar = boolvar(shape=(v + 1))
    #     model += bvar[0] == 1
    #     model += bvar == ((matrix.T[c] <= matrix.T[c + 1]) &
    #                       ((matrix.T[c] < matrix.T[c + 1]) | (bvar[1:] == 1)))
    #     model += bvar[-1] == 0
    # <SYMMETRY_BREAKING_CONSTRAINT_END>

    return model, (matrix,)

# Example usage
model, (matrix,) = bibd(v, b, r, k, l)
model.solve()

# Print
solution = {"matrix": matrix.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script

