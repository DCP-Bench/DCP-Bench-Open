#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/grocery2.mzn

# Data
total_price = 711  # total price in cents
num_items = 4
# End of data

# Import libraries
from cpmpy import *
import json
import numpy as np

# Decision variables (prices are considered in cents)
prices = intvar(1, total_price, shape=num_items)

# Constraints
model = Model()

# The sum of the prices in cents is equal to the total price in cents
model += sum(prices) == total_price

# The product of the prices should equal to the scaled total price in cents (to account for the multiplication)
model += np.prod(prices) == total_price * (100 ** (num_items - 1))

# Solve
model.solve()

# Print the solution
solution = {"prices": prices.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script