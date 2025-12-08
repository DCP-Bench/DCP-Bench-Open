#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob049_number_partitioning.py
# Source description: https://www.csplib.org/Problems/prob049/

"""
This problem consists of finding a partition of numbers 1..N into two sets A and B such that:

- A and B have the same cardinality
- Sum of numbers in A = sum of numbers in B
- Sum of squares of numbers in A = sum of squares of numbers in B

There is no solution for \( N < 8 \).

Here is an example for \( N = 8 \):
A = (1, 4, 6, 7) and B = (2, 3, 5, 8)

Print the sets A and B (A, B).
"""

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
