#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/hardy_1729.mzn

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
