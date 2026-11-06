#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/candies.py

# Data
ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]  # Ratings of the children
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
n = len(ratings)

# variables
x = intvar(1, n, shape=(n,), name="x")  # number of candies for each child
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
