#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/50_puzzle.py
# Source description: http://www.chlond.demon.co.uk/puzzles/puzzles1.html, puzzle nr. 5.

"""
A side show is described as follows: "There were a number of little
dummies which you were to knock over with baseballs. The man said: 'Take as many
throws as you like at a cent apiece and stand as close as you please. Add up the
numbers on all the men that you knock down and when the sum amounts to exactly
a given target sum, neither more nor less you get a genuine prize.'"
The numbers on the dummies are given as a list of integers.

Print the dummies that are knocked over (dummies) as a list of booleans.
"""

# Data
target_sum = 50  # Target sum to achieve
values = [15, 9, 30, 21, 19, 3, 12, 6, 25, 27]  # Numbers on the dummies
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
n = len(values)

# Decision variables
dummies = boolvar(shape=n, name="dummies")  # Boolean array to indicate which dummies are knocked over

# Model
model = Model([
    sum([values[i] * dummies[i] for i in range(n)]) == target_sum
])

# Solve the model
model.solve()

# Print the solution
solution = {"dummies": dummies.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script