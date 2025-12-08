#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob019_magic_sequence.py
# Source description: https://www.csplib.org/Problems/prob019/

"""
A magic sequence of length \( n \) is a sequence of integers \( x_0, \ldots, x_{n-1} \) between 0 and \( n-1 \),
such that for all \( i \) in 0 to \( n-1 \), the number \( i \) occurs exactly \( x_i \) times in the sequence.
For instance, 6, 2, 1, 0, 0, 0, 1, 0, 0, 0 is a magic sequence since 0 occurs 6 times in it, 1 occurs twice, etc.

Print the magic sequence (x).
"""

# Data
n = 12  # Length of the magic sequence
# End of data

# Import libraries
import json
import numpy as np
from cpmpy import *

def magic_sequence(n):
    model = Model()

    x = intvar(0, n - 1, shape=n, name="x")

    # Constraints
    for i in range(n):
        model += x[i] == sum(x == i)

    # Speedup search
    # <SYMMETRY_BREAKING_CONSTRAINT_START>
    # model += sum(x) == n
    # model += sum(x * np.arange(n)) == n
    # <SYMMETRY_BREAKING_CONSTRAINT_END>

    return model, (x,)

# Example usage
model, (x,) = magic_sequence(n)
model.solve()

# Print
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
