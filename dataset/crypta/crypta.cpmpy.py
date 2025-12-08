#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/crypta.py
# Source description: Name: crypta.pl, Title: crypt-arithmetic, Original Source: P. Van Hentenryck's book, Adapted by: Daniel Diaz - INRIA France, Date: September 1992

"""
Cryptarithmetic puzzle, solve the operation:

  B A I J J A J I I A H F C F E B B J E A
   + D H F G A B C D I D B I F F A G F E J E
   -----------------------------------------
   = G J E G A C D D H F A F J B F I H E E F

    where all letters are distinct digits from 0 to 9, and the first letter of each number cannot be zero.

Print the digit of each letter (A, B, C, D, E, F, G, H, I, J).
"""

# Import libraries
from cpmpy import *
import json

model = Model()

# variables
LD = intvar(0, 9, shape=10, name="LD")
A, B, C, D, E, F, G, H, I, J = LD

Sr1 = intvar(0, 1, name="Sr1")
Sr2 = intvar(0, 1, name="Sr2")

#
# constraints
#
model += [AllDifferent(LD)]
model += [B >= 1]
model += [D >= 1]
model += [G >= 1]

model += [A + 10 * E + 100 * J + 1000 * B + 10000 * B + 100000 * E +
          1000000 * F + E + 10 * J + 100 * E + 1000 * F + 10000 * G +
          100000 * A + 1000000 * F == F + 10 * E + 100 * E + 1000 * H +
          10000 * I + 100000 * F + 1000000 * B + 10000000 * Sr1]

model += [C + 10 * F + 100 * H + 1000 * A + 10000 * I + 100000 * I +
          1000000 * J + F + 10 * I + 100 * B + 1000 * D + 10000 * I +
          100000 * D + 1000000 * C + Sr1 == J + 10 * F + 100 * A + 1000 * F +
          10000 * H + 100000 * D + 1000000 * D + 10000000 * Sr2]

model += [A + 10 * J + 100 * J + 1000 * I + 10000 * A + 100000 * B + B +
          10 * A + 100 * G + 1000 * F + 10000 * H + 100000 * D + Sr2 == C +
          10 * A + 100 * G + 1000 * E + 10000 * J + 100000 * G]

# Solve the model
model.solve()

# Print the solution
solution = {"A": A.value(), "B": B.value(), "C": C.value(), "D": D.value(), "E": E.value(), "F": F.value(),
            "G": G.value(), "H": H.value(), "I": I.value(), "J": J.value()}
print(json.dumps(solution))
# End of CPMPy script
