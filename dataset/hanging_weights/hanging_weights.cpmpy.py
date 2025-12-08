#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/hanging_weights.py

"""
Here's a puzzle similar to the one in the puzzle hunt.  The diagram
below is a bunch of weights (A-M) hanging from a system of bars.
Each weight has an integer value between 1 and 13, and the goal is
to figure out what each weight must be for the the diagram below to
balance correctly as shown:

                       |
                       |
           +--+--+--+--+--+--+--+
           |                    |
           |                    |
        +--+--+--+--+--+        |
        |     L        M        |
        |                       |
+--+--+--+--+--+--+     +--+--+--+--+--+
H              |  I     |  J        K  |
              |        |              |
     +--+--+--+--+--+  |     +--+--+--+--+--+
     E              F  |     G              |
                       |                    |
           +--+--+--+--+--+  +--+--+--+--+--+--+
           A              B  C                 D

The rules for this kind of puzzle are:
(1) The weights on either side of a given pivot point must be equal,
  when weighted by the distance from the pivot, and
(2) a bar hanging beneath another contributes it's total weight as
  through it were a single weight.  For instance, the bar on the bottom
  right must have 5*C=D, and the one above it must have 3*G=2*(C+D).

Print the weights (a, b, c, d, e, f, g, h, i, j, k, l, m) that satisfy the conditions above.
"""

# Import libraries
from cpmpy import *
import numpy as np
import json
import math

N = 13
x = intvar(1, N, shape=N, name="x")
a, b, c, d, e, f, g, h, i, j, k, l, m = x

model = Model([
    AllDifferent(x),
    4 * a == b,
    5 * c == d,
    3 * e == 2 * f,
    3 * g == 2 * (c + d),
    3 * (a + b) + 2 * j == k + 2 * (g + c + d),
    3 * h == 2 * (e + f) + 3 * i,
    (h + i + e + f) == l + 4 * m,
    4 * (l + m + h + i + e + f) == 3 * (j + k + g + a + b + c + d)
])

# Solve
model.solve()

# Output
solution = {
    "a": int(a.value()),
    "b": int(b.value()),
    "c": int(c.value()),
    "d": int(d.value()),
    "e": int(e.value()),
    "f": int(f.value()),
    "g": int(g.value()),
    "h": int(h.value()),
    "i": int(i.value()),
    "j": int(j.value()),
    "k": int(k.value()),
    "l": int(l.value()),
    "m": int(m.value())
}
print(json.dumps(solution))
# End of CPMPy script
