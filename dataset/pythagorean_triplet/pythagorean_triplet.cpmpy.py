#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/euler9.py

"""
A Pythagorean triplet is a set of three natural numbers, a  b  c, for which,
a^2 + b^2 = c^2

For example, 3^2 + 4^2 = 9 + 16 = 25 = 5^2.

There exists exactly one Pythagorean triplet for which a + b + c = 1000.

Print a, b, and c (a, b, c) for this Pythagorean triplet such that a + b + c = 1000.
"""

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
