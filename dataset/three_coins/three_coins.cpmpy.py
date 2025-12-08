#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/3_coins.py

"""
Three coins lie on a table in the order tails, heads, tails. In precisely three moves
make them face either all heads or all tails. Each move consists of choosing one coin
and flipping it over.

Print the steps (steps) to make all coins face either all heads or all tails, as a list of lists of booleans, where True means tails -1- and False means heads -0-.
"""

# Data
num_moves = 3  # Number of moves to make all coins face either all heads or all tails
init = [1, 0, 1]  # Initial configuration of the coins, 1 means tails and 0 means heads
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
n = len(init)

# decision variables
# 0: heads, 1: tails
steps = boolvar(shape=(num_moves + 1, n), name="x")  # The steps to make all coins face either all heads or all tails

#  last line, either all heads or all tails
last_val = sum(steps[num_moves])

model = Model([
    steps[0] == init,
    # Exactly one difference per move
    [sum([steps[m, j] != steps[m - 1, j] for j in range(n)]) == 1 for m in range(1, num_moves + 1)],
    # last line: either all heads of all tails
    ((last_val == 0) | (last_val == n)),
])

# Solve the model
model.solve()

# Print the solution
solution = {"steps": steps.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
