#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/send_more_money.py

"""
The "Send More Money" puzzle is a classic cryptarithmetic problem where each letter represents a unique digit. The
goal is to assign digits to the letters such that the following equation holds true:

   SEND
 + MORE
 ------
  MONEY

Each letter must be assigned a unique digit from 0 to 9, and the first letter of each word cannot be zero.

Print the values assigned to each letter (s, e, n, d, m, o, r, y).
"""

# Import libraries
from cpmpy import *
import numpy as np
import json

# Decision variables
s, e, n, d, m, o, r, y = intvar(0, 9, shape=8)

model = Model(
    AllDifferent([s, e, n, d, m, o, r, y]),
    (sum([s, e, n, d] * np.array([1000, 100, 10, 1])) \
     + sum([m, o, r, e] * np.array([1000, 100, 10, 1])) \
     == sum([m, o, n, e, y] * np.array([10000, 1000, 100, 10, 1]))),
    s > 0,
    m > 0,
)

# Solve
model.solve()

# Print
solution = {
    "s": s.value(),
    "e": e.value(),
    "n": n.value(),
    "d": d.value(),
    "m": m.value(),
    "o": o.value(),
    "r": r.value(),
    "y": y.value()
}
print(json.dumps(solution))
# End of CPMPy script
