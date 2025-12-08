#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/hardy_1729.mzn

"""
Find a combination of 4 different numbers between 1 and 100, such that the sum of the squares of the two first
numbers is equal to the sum of the squares of the other two numbers, i.e. a^2 + b^2 = c^2 + d^2 for some a, b, c,
d in {1, 100}, a != b != c != d.

Print the numbers (a, b, c, d).
"""

# Import libraries
from cpmpy import *
import json
import numpy as np

range_min = 1
range_max = 100

# Decision variables
a, b, c, d = intvar(range_min, range_max, shape=4)

# Constraints
model = Model()

# Sum of squares of any two numbers is equal to the sum of squares of the other two numbers
model += (a**2 + b**2) == (c**2 + d**2)

# Constraints to ensure all variables are distinct
model += AllDifferent([a, b, c, d])

# Solve
model.solve()

# Print the solution
solution = {"a": a.value(), "b": b.value(), "c": c.value(), "d": d.value()}
print(json.dumps(solution))
# End of CPMPy script
