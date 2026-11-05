#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/circling_squares.py
# Source description: From the Oz examples http://www.comp.nus.edu.sg/~henz/projects/puzzles/arith/circlingsquares.html from 'Amusements in Mathematics, Dudeney', number 43.

# Import libraries
from cpmpy import *
import json


def s(x1, x2, y1, y2):
    return x1 * x1 + x2 * x2 == y1 * y1 + y2 * y2


n = 10

# variables
x = intvar(1, 99, shape=n, name="x")
A, B, C, D, E, F, G, H, I, K = x

# constraints
model = Model([AllDifferent(x),
               A == 16,
               B == 2,
               F == 8,
               G == 14,

               s(A, B, F, G),
               s(B, C, G, H),
               s(C, D, H, I),
               s(D, E, I, K),
               s(E, F, K, A),
               ])
# End of CPMPy script

# Solve
model.solve()

# Print the solution
solution = {"A": A.value(), "B": B.value(), "C": C.value(), "D": D.value(), "E": E.value(),
            "F": F.value(), "G": G.value(), "H": H.value(), "I": I.value(), "K": K.value()}
print(json.dumps(solution))
# End of CPMPy script
