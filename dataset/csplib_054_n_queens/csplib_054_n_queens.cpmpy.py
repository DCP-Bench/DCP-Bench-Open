#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob054_n_queens.py
# Source description: https://www.csplib.org/Problems/prob054/

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
