#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/broken_weights.py
# Source description: http://www.mathlesstraveled.com/?p=701
# Misc: http://www.hakank.org/cpmpy/cpmpy_hakank.py

# Data
m = 40 # total weight
n = 4 # number of pieces
# End of data

# Import libraries
from cpmpy import *
import json


def increasing_strict(args):
    """
    Ensure that the values in args are strict increasing.
    """
    return [args[i - 1] < args[i] for i in range(1, len(args))]


# variables
weights = intvar(1, m, shape=n, name="weights")
x = intvar(-1, 1, shape=(m, n), name="x")

model = Model()

# constraints

model += [sum(weights) == m]

# Check that all weights from 1 to m can be made.
#
# Since all weights can be on either side
# of the side of the scale we allow either
# -1, 0, or 1 of the weights, assuming that
# -1 is the weights on the left and 1 is on the right.
#
for i in range(m):
    model += [sum([weights[j] * x[i, j] for j in range(n)]) == i + 1]
    # model += [i+1 == sum(weights * x[i])] # using numpy's magic

# symmetry breaking
# <SYMMETRY_BREAKING_CONSTRAINT_START>
# # for j in range(1, n):
# #   model += [weights[j-1] < weights[j]]
# model += [increasing_strict(weights)]
# <SYMMETRY_BREAKING_CONSTRAINT_END>

model.solve()

# Print the solution
solution = {"weights": weights.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
