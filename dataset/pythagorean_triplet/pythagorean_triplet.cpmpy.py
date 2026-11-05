#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/euler9.py

# Import libraries
from cpmpy import *
import json

a, b, c = intvar(1, 500, shape=3, name="x")

model = Model([
    a + b + c == 1000,
    a * a + b * b == c * c
])

model.solve()

solution = {"a": a.value(), "b": b.value(), "c": c.value()}
print(json.dumps(solution))
# End of CPMPy script
