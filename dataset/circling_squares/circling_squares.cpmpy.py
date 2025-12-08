#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/circling_squares.py
# Source description: From the Oz examples http://www.comp.nus.edu.sg/~henz/projects/puzzles/arith/circlingsquares.html from 'Amusements in Mathematics, Dudeney', number 43.

"""
Circling the squares:

The puzzle is to place a different number in each of the ten squares so that the sum of the squares of any two
adjacent numbers shall be equal to the sum of the squares of the two numbers diametrically opposite to them. The four
numbers placed, as examples, must stand as they are. The square of 16 is 256, and the square of 2 is 4. Add these
together, and the result is 260. Also—the square of 14 is 196, and the square of 8 is 64. These together also make
260. Now, in precisely the same way, B and C should be equal to G and H (the sum will not necessarily be 260),
A and K to F and E, H and I to C and D, and so on, with any two adjoining squares in the circle.

All you have to do is to fill in the remaining six numbers. Fractions are not allowed, and I shall show that no
number need contain more than two figures.

Print the 10 numbers in the circle (A, B, C, D, E, F, G, H, I, K) when A=16, B=2, F=8, G=14.
"""

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
