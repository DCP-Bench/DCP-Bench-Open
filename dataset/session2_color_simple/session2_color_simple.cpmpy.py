#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/color_simple.mzn

"""
We want to assign a different colour to the following countries: Belgium, Denmark, France, Germany, Netherlands
and Luxembourg. Two neighbouring countries cannot have the same colour. You can use integers starting from 1 to
represent the colours. Find a colouring that minimizes the number of colours used.

Print the colour assigned to each country as a list (colors) of 6 integers. Each colour is represented by an integer
starting from 1, where the first colour is 1, the second is 2, and so on.
"""

# Data
graph = [  # the adjacency of the countries, (i, j) means that country i is adjacent to country j
    [3, 1],
    [3, 6],
    [3, 4],
    [6, 4],
    [6, 1],
    [1, 5],
    [1, 4],
    [4, 5],
    [4, 2]
]
# End of data

# Import libraries
from cpmpy import *
import json

num_edges = 9
num_nodes = 6

# Decision Variables
colors = intvar(1, num_nodes, shape=num_nodes)  # the colour assigned to each country

# Constraints
model = Model()

# Two neighbouring countries cannot have the same colour
for i, j in graph:
    # Python uses 0-based indexing, but the countries are 1-based, so we need to subtract 1 from the indices
    model += colors[i - 1] != colors[j - 1]

# Objective
# Find a colouring that minimizes the number of colours used
model.minimize(max(colors))

# Solve
model.solve()

# Print the solution
solution = {"colors": colors.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
