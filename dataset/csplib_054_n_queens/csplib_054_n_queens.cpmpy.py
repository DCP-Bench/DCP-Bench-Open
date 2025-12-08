#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob054_n_queens.py
# Source description: https://www.csplib.org/Problems/prob054/

"""
Can \( n \) queens (of the same color) be placed on a \( n \times n \) chessboard so that none of the queens can attack
each other? In chess, a queen attacks other squares on the same row, column, or either diagonal as itself. So the
\( n \)-queens problem is to find a set of \( n \) locations on a chessboard, no two of which are on the same row,
column or diagonal.

Print the positions of the queens on the chessboard (queens) as a list of n integers - ranging from 1 to n, where the i-th
integer represents the column position of the queen in the i-th row.
"""

# Data
n = 10  # Size of the chessboard and number of queens
# End of data

# Import libraries
import json
import numpy as np
from cpmpy import *

def n_queens(n=8):

    queens = intvar(1, n, shape=n, name="queens")

    # Constraints on columns and left/right diagonal
    model = Model([
        AllDifferent(queens),
        AllDifferent(queens - np.arange(n)),
        AllDifferent(queens + np.arange(n)),
    ])

    return model, (queens,)

# Example usage
model, (queens,) = n_queens(n)
model.solve()

# Print
solution = {"queens": queens.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
