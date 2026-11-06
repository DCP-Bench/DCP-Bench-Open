#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob076_costas_arrays.py
# Source description: https://www.csplib.org/Problems/prob076/

# Data
n = 8  # Size of the Costas array
# End of data

# Import libraries
import json
import numpy as np
from cpmpy import *

def costas_array(n=6):
    model = Model()

    # Declare variables
    costas = intvar(1, n, shape=n, name="costas")
    differences = intvar(-n + 1, n - 1, shape=(n, n), name="differences")

    tril_idx = np.tril_indices(n, -1)
    triu_idx = np.triu_indices(n, 1)

    # Constraints
    # Fix the values in the lower triangle in the difference matrix to -n+1.
    model += differences[tril_idx] == -n + 1

    model += [AllDifferent(costas)]

    # Define the differences
    for i, j in zip(*triu_idx):
        model += [differences[i, j] == costas[j] - costas[j - i - 1]]

    # All entries in a particular row of the difference triangle must be distinct
    for i in range(n - 2):
        model += [AllDifferent([differences[i, j] for j in range(n) if j > i])]

    # Additional constraints to speed up the search
    # <SYMMETRY_BREAKING_CONSTRAINT_START>
    # model += differences[triu_idx] != 0
    # for k, l in zip(*triu_idx):
    #     if k < 2 or l < 2:
    #         continue
    #     model += [differences[k - 2, l - 1] + differences[k, l] ==
    #               differences[k - 1, l - 1] + differences[k - 1, l]]
    # <SYMMETRY_BREAKING_CONSTRAINT_END>

    return model, (costas, differences)

# Example usage
model, (costas, differences) = costas_array(n)
model.solve()

# Print
solution = {
    "costas": costas.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script
