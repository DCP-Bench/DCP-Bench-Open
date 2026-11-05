#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob005_auto_correlation.py
# Source description: https://www.csplib.org/Problems/prob005/

# Data
n = 10  # Length of the binary sequence
# End of data

# Import libraries
from cpmpy import *
import numpy as np
import json


# periodic auto correlation
def PAF(arr, s):
    # roll the array 's' indices
    return sum(arr * np.roll(arr, -s))


# Decision Variables
sequence = intvar(-1, 1, shape=n, name="sequence")  # binary sequence
E = sum([PAF(sequence, s) ** 2 for s in range(1, n)])  # energy value

model = Model()

# exclude 0
model += sequence != 0

# minimize sum of squares
model.minimize(E)

# Solve
model.solve()

# Print
solution = {"sequence": sequence.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
