#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob084_hadamard_matrix.py
# Source description: https://www.csplib.org/Problems/prob084/

# Data
l = 9  # Value of l (must be an odd positive integer)
# End of data

# Import libraries
import json
import numpy as np
from cpmpy import *

def PAF(arr, s):
    return sum(arr * np.roll(arr,-s))

def hadamard_matrix(l=5):

    m = int((l - 1) / 2)

    a = intvar(-1,1, shape=l, name="a")
    b = intvar(-1,1, shape=l, name="b")

    model = Model()

    model += a != 0 # exclude 0 from dom
    model += b != 0 # exclude 0 from dom

    model += sum(a) == 1
    model += sum(b) == 1

    for s in range(1,m+1):
        model += (PAF(a,s) + PAF(b,s)) == -2

    return model, (a,b)


# Example usage
model, (a, b) = hadamard_matrix(l)
model.solve()

# Print
solution = {"a": a.value().tolist(), "b": b.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
