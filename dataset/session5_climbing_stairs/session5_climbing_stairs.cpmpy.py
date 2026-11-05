#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/climbing_stairs.mzn

# Data
n = 20  # total number of steps in the stair
m1, m2 = 3, 5  # number of steps that can be taken at a time
# End of data

# Import libraries
from cpmpy import *
import json
import numpy as np

# Decision variables
# In the worst case, we take all steps one at a time, so we have 'n' decision variables
steps = intvar(0, m2, shape=n)  # steps taken at each move

# Model setup
model = Model()

# Constraint: the sum of steps should equal the total number of stairs
model += sum(steps) == n

# Constraint: the number of steps taken at each move should be between m1 and m2 or 0
model += [(steps[i] >= m1) | (steps[i] == 0) for i in range(n)]
model += [steps[i] <= m2 for i in range(n)]

# Trailing zeros: If a step is 0, then all the following steps should be 0
for i in range(1, n):
    model += (steps[i - 1] == 0).implies(all(steps[j] == 0 for j in range(i, n)))

# Solve
model.solve()

# Print the solution
solution = {"steps": steps.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script