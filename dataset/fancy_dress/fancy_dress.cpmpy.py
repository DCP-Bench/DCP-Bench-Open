#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/fancy.py

# Import libraries
from cpmpy import *
import json

# variables
# t: tie
# h: hat
# r: shirt
# s: socks
# n: entrance fee
t = boolvar(name="t")
h = boolvar(name="h")
r = boolvar(name="r")
s = boolvar(name="s")
n = boolvar(name="n")
cost = intvar(0, 100, name="cost")

model = Model(minimize=cost)

model += [t.implies(r) | n]

model += [((s | r).implies(t | h)) | n]

model += [(r | h | ~s).implies(t | n)]

model += [cost == 10 * t + 2 * h + 12 * s + 11 * n]

model.solve()

solution = {"t": t.value(), "h": h.value(), "r": r.value(), "s": s.value(), "n": n.value()}
print(json.dumps(solution))
# End of CPMPy script
