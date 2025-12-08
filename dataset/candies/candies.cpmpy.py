#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/candies.py

"""
Alice is a kindergarden teacher. She wants to give some candies to the
children in her class. All the children sit in a line, and each of
them has a rating score according to their usual performance.
Alice wants to give at least 1 candy for each child. Children get
jealous of their immediate neighbors, so if two children sit next
to each other, then the one with the higher rating must get more
candies. Alice wants to save money, so she wants to minimize the
total number of candies.

Print the optimal number of candies needed in total (z) and the
number of candies for each child (x) as a list of integers.
"""

# Data
ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]  # Ratings of the children
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
n = len(ratings)

# variables
x = intvar(1, n, shape=n, name="x")  # number of candies for each child
z = intvar(1, n * n, name="z")  # total number of candies

# constraints
model = Model([z == sum(x),
               z >= n])

for i in range(1, n):
    if ratings[i - 1] > ratings[i]:
        model += (x[i - 1] > x[i])
    elif ratings[i - 1] < ratings[i]:
        model += (x[i - 1] < x[i])

model.minimize(z)
# Solve the model
model.solve()

# Print the solution
solution = {"z": z.value(), "x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
