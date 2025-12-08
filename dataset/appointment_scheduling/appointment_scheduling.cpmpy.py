#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/appointment_scheduling.py
# Source description: http://stackoverflow.com/questions/11143439/appointment-scheduling-algorithm-n-people-with-n-free-busy-slots-constraint-sa

"""
Schedule 4 people into 4 interview slots based on their free-busy schedules.

Print the assignment of people to slots (x) as a list of lists of booleans, where x[i][j] is True if person i is assigned to slot j, and False otherwise.
"""

# Data
m = [
    [1, 1, 1, 1],
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1]
]  # Matrix representing the free-busy schedules
# End of data

# Import libraries
from cpmpy import *
import json
import random

model = Model()

n = len(m)

# decision variables

# the assignment of persons to a slot (appointment number 0..n)
x = boolvar(shape=(n, n), name="x")

# constraints

for i in range(n):
    # ensure a free slot
    model += (sum([m[i][j] * x[(i, j)] for j in range(n)]) == 1)

    # ensure one assignment per slot
    model += (sum([x[(i, j)] for j in range(n)]) == 1)
    model += (sum([x[(j, i)] for j in range(n)]) == 1)
# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
