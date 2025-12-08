#!/usr/bin/python3
# Category: complex_or
# Source: https://github.com/xzymustbexzy/Chain-of-Experts/blob/main/dataset/ComplexOR/cutting_stock

"""
This is a cutting stock problem. Given a roll of width `RollWidth` and a set of widths to be cut. Each width
has a certain number of Orders. There are `NumPatterns` patterns and each pattern has a certain number
of rolls of each width. The problem aims to minimize the total number of raw rolls cut. It is
constrained that for each width, the total number of rolls cut meets the total Orders. How to decide the number of
rolls cut using each patter?

Print the number of times each cutting pattern is used (patterns_used) as a list of integers, and the total number of raw rolls cut (min_rolls_cut) as an integer.
"""

# Data
roll_width = 10 # The width of the raw rolls
widths = [2, 3, 5] # The widths of the smaller pieces to be cut
orders = [4, 2, 2] # orders[i] is the number of pieces of width widths[i] needed
num_patterns = 2 # The number of available cutting patterns
num_rolls_width = [
    [1, 2, 0], # num_rolls_width[i][j] is the number of pieces of width widths[j] in pattern i
    [0, 0, 1]
]
# End of data

# Import libraries
from cpmpy import *
import json

# Data unpacking
num_rolls_width = cpm_array(num_rolls_width)

num_item_widths = len(widths)

# Decision variables
patterns_used = intvar(0, 100, shape=num_patterns, name="patterns_used") # Number of times each pattern is used

# Model
model = Model()

# Constraint 1: For each width, the total number of rolls cut meets the total orders
for i in range(num_item_widths):
    model += sum(num_rolls_width[j, i] * patterns_used[j] for j in range(num_patterns)) >= orders[i]

# Objective: Minimize the total number of raw rolls cut
min_rolls_cut = sum(patterns_used)
model.minimize(min_rolls_cut)

# Solve the model
model.solve()

# Print the solution
solution = {
    "patterns_used": patterns_used.value().tolist(),
    "min_rolls_cut": int(model.objective_value())
}
print(json.dumps(solution))
# End of CPMPy script