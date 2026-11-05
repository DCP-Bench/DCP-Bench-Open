#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob049_number_partitioning.py
# Source description: https://www.csplib.org/Problems/prob049/

# Data
n = 8  # The number N
# End of data

# Import libraries
import json
import numpy as np
from cpmpy import *

def number_partitioning(n=8):
    assert n % 2 == 0, "The value of n must be even"

    # x[i] is the ith value of the first set
    x = intvar(1, n, shape=n // 2)

    # y[i] is the ith value of the second set
    y = intvar(1, n, shape=n // 2)

    model = Model()

    model += AllDifferent(np.append(x, y))

    # sum of numbers is equal in both sets
    model += sum(x) == sum(y)

    # sum of squares is equal in both sets
    model += sum(x ** 2) == sum(y ** 2)

    # break symmetry
    # <SYMMETRY_BREAKING_CONSTRAINT_START>
    # model += x[:-1] <= x[1:]
    # model += y[:-1] <= x[1:]
    # <SYMMETRY_BREAKING_CONSTRAINT_END>

    return model, (x,y)

# Example usage
model, (x, y) = number_partitioning(n)
model.solve()

A = x
B = y

# Print
solution = {"A": x.value().tolist(), "B": y.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
