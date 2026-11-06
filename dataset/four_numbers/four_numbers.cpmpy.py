#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/four_numbers.py

# Data
numbers = [7, 8, 9, 10]
# End of data

# Import libraries
from cpmpy import *
import numpy as np
import json


def increasing(args):
    """
    Ensure that the values in args are increasing.
    """
    return [args[i - 1] <= args[i] for i in range(1, len(args))]


model = Model()

m = len(numbers)
n = 3

x = intvar(1, 10, shape=n, name="x")
# coefficient matrix
tmp = boolvar(shape=(m, n), name="tmp")

for i in range(m):
    model += [sum([tmp[i, j] * x[j] for j in range(n)]) == numbers[i]]

# <SYMMETRY_BREAKING_CONSTRAINT_START>
# model += [increasing(x)]
# <SYMMETRY_BREAKING_CONSTRAINT_END>

model.solve()

solution = {
    "x": x.value().tolist()
}

print(json.dumps(solution))
# End of CPMPy script
