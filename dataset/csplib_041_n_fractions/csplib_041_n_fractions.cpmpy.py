#!/usr/bin/python3
# Category: csplib
# Source: https://www.hakank.org/cpmpy/fractions_model.py
# Source description: https://www.csplib.org/Problems/prob041/

"""
Find distinct non-zero digits such that the following equation holds: A / BC + D / EF + G / HI = 1
Here, BC, EF, and HI are two-digit numbers formed by B and C, E and F, and H and I, respectively.

Print the values (A, B, C, D, E, F, G, H, I) that satisfy the equation above.
"""

# Import libraries
from cpmpy import *
import numpy as np
import json

# There is no data for this problem

# Variables
n = 9
x = intvar(1, n, shape=9, name="x")
A, B, C, D, E, F, G, H, I = x

D1 = intvar(1, n * n, name="D1")
D2 = intvar(1, n * n, name="D2")
D3 = intvar(1, n * n, name="D3")

# Constraints
model = Model([AllDifferent(x),
               D1 == 10 * B + C,
               D2 == 10 * E + F,
               D3 == 10 * H + I,
               A * D2 * D3 + D * D1 * D3 + G * D1 * D2 == D1 * D2 * D3
               ])

# Solve
model.solve()

# Output
solution = {
    "A": int(A.value()),
    "B": int(B.value()),
    "C": int(C.value()),
    "D": int(D.value()),
    "E": int(E.value()),
    "F": int(F.value()),
    "G": int(G.value()),
    "H": int(H.value()),
    "I": int(I.value())
}
print(json.dumps(solution))
# End of CPMPy script