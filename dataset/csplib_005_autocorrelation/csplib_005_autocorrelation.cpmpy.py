#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob005_auto_correlation.py
# Source description: https://www.csplib.org/Problems/prob005/

"""
These problems have many practical applications in communications and electrical engineering. The objective is to
construct a binary sequence of length n that minimizes the autocorrelations between bits. Each bit in the sequence
takes the value +1 or -1. With non-periodic (or open) boundary conditions, the k-th autocorrelation, Ck is defined to
be \[ C_k = \sum_{i=0}^{n-k-1} S_i \cdot S_{i+k} \]. With periodic (or cyclic) boundary conditions, the k-th
autocorrelation, Ck is defined to be \[ C_k = \sum_{i=0}^{n-1} S_i \cdot S_{(i+k) \mod n} \]. The aim is to
minimize the sum of the squares of these autocorrelations. That is, to minimize \[ E = \sum_{k=1}^{n-1} C_k^2 \].

Print the binary sequence (sequence) as a list of integers, where -1 represents a bit value of -1 and 1 represents a bit value of +1.
"""

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
