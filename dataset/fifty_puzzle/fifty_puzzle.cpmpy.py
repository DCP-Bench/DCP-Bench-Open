#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/50_puzzle.py
# Source description: http://www.chlond.demon.co.uk/puzzles/puzzles1.html, puzzle nr. 5.

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