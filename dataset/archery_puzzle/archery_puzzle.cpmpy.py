#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/archery_puzzle.py

# Data
targets = [16, 17, 23, 24, 39, 40]
target_score = 100
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
n = len(targets)

# Decision variables
hits = intvar(0, target_score, shape=n, name="hits")
score = intvar(0, target_score * 2, name="score")
deviation = intvar(0, target_score * 2, name="deviation")

# Model
model = Model([
    score == sum(hits * targets),
    deviation == abs(target_score - score)
])

# Objective
model.minimize(deviation)

# Solve the model
model.solve()

# Print the solution
solution = {"hits": hits.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script