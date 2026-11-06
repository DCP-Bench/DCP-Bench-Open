#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob050_diamond_free.py
# Source description: https://www.csplib.org/Problems/prob050/

# Data
N = 10  # Number of vertices in the graph
# End of data

# Import libraries
import json
import numpy as np
from cpmpy import *
from itertools import combinations

def diamond_free(N):
    # By definition a and b will have the same cardinality:
    matrix = boolvar(shape=(N, N), name="matrix")

    model = Model()

    # No rows contain just zeroes.
    model += [sum(row) > 0 for row in matrix] # can be written cleaner, see issue #117
    # Every row has a sum modulo 3.
    model += [sum(row) % 3 == 0 for row in matrix]
    # The sum of the matrix is modulo 12.
    model += sum(matrix) % 12 == 0
    # No row R contains a 1 in its Rth column.
    model += [matrix[np.diag_indices(N)] == 0]

    # Every grouping of 4 rows can have at most a sum of 4 between them.
    for a, b, c, d in combinations(range(N), 4):
        model += sum([matrix[a][b], matrix[a][c], matrix[a][d],
                      matrix[b][c], matrix[b][d], matrix[c][d]]) <= 4

    # Undirected graph
    model += matrix == matrix.T

    return model, matrix

# Example usage
model, matrix = diamond_free(N)
model.solve()

# Print
solution = {"matrix": matrix.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
