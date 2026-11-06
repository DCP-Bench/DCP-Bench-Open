#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/send_more_money.py

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
