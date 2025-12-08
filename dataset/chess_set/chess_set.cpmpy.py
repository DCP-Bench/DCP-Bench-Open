#!/usr/bin/python3
# Category: hakan_examples
# Source: http://www.hakank.org/cpmpy/chess_set.py
# Source description: Applications of Optimization with XPress-MP.pdf page 11. The problem is presented on page 7.

"""
A small joinery makes two different sizes of boxwood chess sets. The small set requires 3 hours of machining on a
lathe, and the large set requires 2 hours. There are four lathes with skilled operators who each work a 40 hour week,
so we have 160 lathe-hours per week. The small chess set requires 1 kg of boxwood, and the large set requires 3 kg.
Unfortunately, boxwood is scarce and only 200 kg per week can be obtained. When sold, each of the large chess sets
yields a profit of $20, and one of the small chess set has a profit of $5. The problem is to decide how many sets of
each kind should be made each week so as to maximize profit.

Print the number of small sets and large sets, and the maximum profit (small_set, large_set, max_profit).
"""

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
