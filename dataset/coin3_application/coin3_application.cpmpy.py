#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/coins3.py
# Source description: From 'Constraint Logic Programming using ECLiPSe' pages 99f and 234 ff. The solution in ECLiPSe is at page 236.

"""
Find the minimum number of coins that allows one to pay exactly any amount smaller than a given maximum amount using a given set of
denominations.

Print the number of each type of coin used (x) as a list of integers.
"""

# Data
denominations = [1, 2, 5, 10, 20, 50]  # Euro cent denominations
max_amount_to_pay = 100  # maximum amount to pay in cents
# End of data

# Import libraries
from cpmpy import *
import json

# Parameters
n = len(denominations)

# declare variables
x = intvar(0, max_amount_to_pay, shape=n, name="x")  # The number of each type of coin used
num_coins = intvar(0, max_amount_to_pay, name="num_coins")  # The total number of coins used

model = Model(minimize=num_coins)

# constraints

# number of used coins, to be minimized
model += [num_coins == sum(x)]

# Check that all changes from 1 to max_amount_to_pay - 1 can be made.
for j in range(1, max_amount_to_pay):
    tmp = intvar(0, max_amount_to_pay, shape=n)
    model += [sum(tmp * denominations) == j]
    model += [tmp[i] <= x[i] for i in range(n)]

# Solve the model
model.solve()

# Print the solution
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script