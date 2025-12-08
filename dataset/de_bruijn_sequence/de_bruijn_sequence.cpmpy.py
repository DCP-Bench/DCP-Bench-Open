#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/debruijn.py

"""
In combinatorial mathematics, a de Bruijn sequence of order n on a size-k alphabet A is a cyclic sequence in which every
possible length-n string on A occurs exactly once as a substring. Such a sequence is denoted by B(k, n) and has length
k^n.

Print the de Bruijn sequence (de_bruijn) of a given order on a given size alphabet as a list of integers.
"""

# Data
base = 2 # size of the alphabet
n = 4 # order
# End of data

# Import libraries
from cpmpy import *
import json

m = base ** n

x = intvar(0, (base ** n) - 1, shape=m)  # all possible numbers
binary = intvar(0, base - 1, shape=(m, n))
de_bruijn = intvar(0, base - 1, shape=m)  # the de Bruijn sequence

model = Model()

model += [AllDifferent(x)]

# convert x[i] <-> binary[i,..]
model += [[x[i] == sum([binary[i][j] * (base ** (n - j - 1)) for j in range(n)]) for i in range(m)]]

# de Bruijn property for the nodes
model += [[binary[i - 1][j] == binary[i][j - 1] for j in range(1, n) for i in range(1, m)]]

# ... and around the corner
model += [[binary[m - 1][j] == binary[0][j - 1] for j in range(1, n)]]

# convert binary -> de_bruijn
model += [[de_bruijn[i] == binary[i][0] for i in range(m)]]

# symmetry breaking: x[1] is the minimum number
# <SYMMETRY_BREAKING_CONSTRAINT_START>
# model += [[x[0] < x[i] for i in range(1, m)]]
# <SYMMETRY_BREAKING_CONSTRAINT_END>

# Solve the model
model.solve()

# Print the solution
solution = {"de_bruijn": de_bruijn.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script