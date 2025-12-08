#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/capital_budget.py
# Source description: Winston 'Operations Research', page 478: Capital budgeting

"""
A company is considering a number of investments. Each investment will yield a net present value (NPV). Each investment requires a
certain cash outflow at the present time. There is a total budget available for investment. How to maximize the NPV obtained from
the investments?

Print whether each investment is chosen (x) as a list of booleans,
and the total NPV (z) as an integer.
"""

# Data
budget = 14000
npv = [16000, 22000, 12000, 8000]
cash_flow = [5000, 7000, 4000, 3000]
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
n = len(npv)

# variables
x = boolvar(shape=n, name="x")  # x[i] = 1 if investments i
z = intvar(0, sum(npv), name="z")  # total NPV

# constraints
model = Model([
    # the sum of all choosen investments must be less than the budget
    sum(x * cash_flow) <= budget,
    z == sum(x * npv)
])

# Objective: maximize the NPV
model.maximize(z)

# Solve the model
model.solve()

# Print the solution
solution = {"z": z.value(), "x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script