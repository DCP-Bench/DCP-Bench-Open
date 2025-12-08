#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/bowls_and_oranges.py
# Source description: http://surana.wordpress.com/2011/06/01/constraint-programming-example/
# Misc: http://www.hakank.org/cpmpy/cpmpy_hakank.py

"""
You have a number of bowls, all placed in a line at exact intervals of
1 meter. You also have a number of oranges. You wish to place all the oranges
in the bowls, no more than one orange in each bowl, so that there are
no three oranges A, B, and C such that the distance between A and B is
equal to the distance between B and C.

Print a solution to the problem as a list of numbers representing the bowls in which the oranges
are placed (x)."""

# Data
n = 40  # Number of bowls
m = 9  # Number of oranges
# End of data

# Import libraries
from cpmpy import *
import json

# Decision variables
x = intvar(1, n, shape=m, name="x")


def increasing(args):
    """
    Ensure that the values in args are increasing.
    """
    return [args[i - 1] <= args[i] for i in range(1, len(args))]


# Model
model = Model([
    AllDifferent(x),
    # <SYMMETRY_BREAKING_CONSTRAINT_START>
    # increasing(x)
    # <SYMMETRY_BREAKING_CONSTRAINT_END>
])

# Constraint to ensure no three oranges A, B, and C have equal distances
for i in range(m):
    for j in range(m):
        for k in range(m):
            if i < j < k:
                model += ((x[j] - x[i]) != (x[k] - x[j]))

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script