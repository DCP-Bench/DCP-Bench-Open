#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/hanging_weights.py

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
