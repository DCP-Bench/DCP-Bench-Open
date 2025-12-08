#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/five_brigands.py
# Source description: From http://www.comp.nus.edu.sg/~henz/projects/puzzles/arith/index.html, The Five Brigands from 'Amusements in Mathematics, Dudeney', number 133.

"""
The five Spanish brigands, Alfonso, Benito, Carlos, Diego, and Esteban,
were counting their spoils after a raid, when it was found that they
had captured altogether exactly 200 doubloons. One of the band pointed
out that if Alfonso had twelve times as much, Benito three times as
much, Carlos the same amount, Diego half as much, and Esteban one-
third as much, they would still have altogether just 200 doubloons.
How many doubloons had each? Also, no brigand had less than one doubloon.

Print the number of doubloons that each brigand may have according to the above information (A, B, C, D, E).
"""

from cpmpy import *
import json

A, B, C, D, E = x = intvar(1, 200, shape=5, name="x")

model = Model([
    A + B + C + D + E == 200,
    6 * (A * 12 + B * 3 + C) + 3 * D + 2 * E == 6 * 200,
])

model.solve()

solution = {"A": A.value(), "B": B.value(), "C": C.value(), "D": D.value(), "E": E.value()}
print(json.dumps(solution))
