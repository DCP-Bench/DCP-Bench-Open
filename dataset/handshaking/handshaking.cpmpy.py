#!/usr/bin/python3
# Category: hakan_examples
# Source: https://www.hakank.org/cpmpy/handshaking.py

"""
Hilary and Jocelyn are married. They invite a number of couples who are friends for dinner. When
they arrive, they shake hands with each other. Nobody shakes hands with him or herself
or with his or her spouse. After there has been some handshaking, Jocelyn jumps up on
a chair and says 'Stop shaking hands!', and then asks how many hands each person has
shaken. All the answers are different.

Print the number of hands Hilary has shaken (hil).
"""

# Data
num_couples = 8  # number of couples invited, i.e., excluding Hilary and Jocelyn
# End of data

# Import libraries
from cpmpy import *
import numpy as np
import json
import math

n = 2 + num_couples * 2

# variables
# can shake max n-2 hands
#   coded Pair1a,Pair1b,  Pair2a,Pair2b, ...
x = intvar(0, n - 2, shape=n, name="x")  # number of hands shaken by each person
hil = x[0]  # Hilary

# who shake with whom:
#  (not him/herself and not his/her spouse)
y = boolvar(shape=(n, n), name="y")
y_flat = [y[i, j] for i in range(n) for j in range(n)]

model = Model()

# constraints

# We assumed that Hilary is in position x[0] and Hilary's spouse - Jocelyn - in x[1]
# All except Hilary's counts are different.
model += [AllDifferent(x[1:])]

for i in range(math.ceil(n / 2)):
    # don't shake hand with spouse
    model += [y[2 * i, 2 * i + 1] == 0,
              y[2 * i + 1, 2 * i] == 0]

for i in range(n):
    model += [y[i, i] == 0,  # don't shake hand with oneself
              x[i] == y[i].sum()  # how many hands has x[i] shaken
              ]

for i in range(n):
    for j in range(n):
        # symmetry of handshaking:
        #    a shake hands with b <-> b shake hands with a
        model += [y[i,j] == y[j,i]]

# Solve
model.solve()

# Output
solution = {
    "hil": hil.value()
}
print(json.dumps(solution))
# End of CPMPy script