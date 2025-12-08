#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/fancy.py

"""
Mr. Greenfan wants to give a dress party where the male guests
must wear green dresses. The following rules are given:
  1 If someone wears a green tie he has to wear a green shirt.
  2 A guest may only wear green socks and a green shirt
    if he wears a green tie or a green hat.
  3 A guest wearing a green shirt or a green hat or who does
    not wear green socks must wear a green tie.
  4 A guest who is not dressed according to rules 1-3 must
    pay a $11 entrance fee.
Mr Greenguest wants to participate but owns only a green shirt
(otherwise he would have to pay one for $9). He could buy
a green tie for $10, a green hat (used) for $2 and green socks
for $12.
What is the cheapest solution for Mr Greenguest to participate?

Print the choices as 0/1 values for tie (t), hat (h), shirt (r), socks (s) and entrance fee (n), such that the total cost is minimized.
"""

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
