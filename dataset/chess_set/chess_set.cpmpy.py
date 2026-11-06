#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/chess_set.py
# Source description: Applications of Optimization with XPress-MP.pdf page 11. The problem is presented on page 7.

# Import libraries
from cpmpy import *
import json

# Decision variables
small_set = intvar(0, 100, name="small_set")
large_set = intvar(0, 100, name="large_set")
max_profit = intvar(0, 10000, name="max_profit")

# Model
model = Model([
    small_set + 3 * large_set <= 200,  # Boxwood constraint
    3 * small_set + 2 * large_set <= 160,  # Lathe-hours constraint
    max_profit == 5 * small_set + 20 * large_set  # Profit calculation
])

# Objective: maximize the profit
model.maximize(max_profit)

# Solve the model
model.solve()

# Print the solution
solution = {
    "small_set": small_set.value(),
    "large_set": large_set.value(),
    "max_profit": max_profit.value()
}
print(json.dumps(solution))
# End of CPMPy script
