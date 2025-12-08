#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/giant_cat_army_riddle.py

"""
Basically you start with [0], then you build this list by using one of three
operations: adding 5, adding 7, or taking sqrt. You successfully complete the
game when you have managed to build a list such that 2,10 and 14 appear
on the list, in that order, and there can be other numbers between them.

The rules also require that all the elements are distinct, they're all <=60
and are all only integers. For example, starting with [0], you can
apply (add5, add7, add5), which would result in [0, 5, 12, 17], but since
it doesn't have 2,10,14 in that order it doesn't satisfy the game.

Print the sequence of integers (x) that satisfies the above conditions in the correct order starting from 0, ending with 14, and has length of 24.
"""

# Import libraries
from cpmpy import *
import numpy as np
import json

maxval = 60
n = 24

# variables
x = intvar(0, maxval, shape=n, name="x")

model = Model([AllDifferent(x)])

# Given
model += [x[0] == 0]

# x[1] == 5 || x[1] == 7
model += [(x[1] == 5) | (x[1] == 7)]
model += (x[n - 1] == 14)

for i in range(n - 1):
    model += [(x[i + 1] == x[i] + 5) |
              (x[i + 1] == x[i] + 7) |
              (x[i] == x[i + 1] * x[i + 1])]

# 0 .. 2 .. 10 .. 14
ix2 = intvar(1, n, name="ix2")
ix10 = intvar(1, n, name="ix10")
model += [2 == x[ix2]]
model += [10 == x[ix10]]
model += [ix2 < ix10]

# Solve
model.solve()

# Output
solution = {
    "x": x.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script
