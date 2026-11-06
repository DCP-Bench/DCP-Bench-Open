#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/five_brigands.py
# Source description: From http://www.comp.nus.edu.sg/~henz/projects/puzzles/arith/index.html, The Five Brigands from 'Amusements in Mathematics, Dudeney', number 133.

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
