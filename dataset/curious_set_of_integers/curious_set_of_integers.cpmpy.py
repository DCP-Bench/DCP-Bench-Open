#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/curious_set_of_integers.py
# Source description: Martin Gardner (February 1967).

"""
The integers 1,3,8, and 120 form a set with a remarkable property: the
product of any two integers is one less than a perfect square. Find
a fifth number (larger than or equal to 0) that can be added to the set without destroying
this property.

Print this number (number).
"""

# Import libraries
from cpmpy import *
import json


model = Model()

# data
n = 5
max_val = 10000

# variables
x = intvar(0, max_val, shape=n)
number = x[-1]

# constraints
model += [AllDifferent(x)]
model += x[0] == 1
model += x[1] == 3
model += x[2] == 8
model += x[3] == 120

for i in range(n):
    for j in range(n):
        if i != j:
            p = intvar(0, max_val)  # the root of the product of x[i] and x[j] plus one
            model += [p * p == x[i] * x[j] + 1]  # the product of any two integers is one less than a perfect square

# Solve the model
model.solve()

# Print the solution
solution = {"number": number.value()}
print(json.dumps(solution))
# End of CPMPy script
