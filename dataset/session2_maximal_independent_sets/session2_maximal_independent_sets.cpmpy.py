#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/maximal_independent_sets.mzn

"""
In graph theory, an independent set is a set of vertices in a graph, no two of which are adjacent. A maximal
independent set is an independent set that is not a subset of any other independent set. A graph may have many
maximal independent sets of widely varying sizes: find a maximal independent set for the data provided. The data
provides an array containing for each node of the graph the set of adjacent nodes.

Print whether each node is included in the maximal independent set (nodes), as a list of booleans.
"""

# Data
n = 8  # number of nodes in the graph
adjacency_list = [  # adjacency list for each node in the graph (1-based)
    [2, 3, 7],
    [1, 4, 8],
    [1, 4, 5],
    [2, 3, 6],
    [3, 6, 7],
    [4, 5, 8],
    [1, 5, 8],
    [2, 6, 7]
]
# End of data

# Import libraries
from cpmpy import *
import json


# Create a binary decision variable for each node to indicate if it's included in the independent set
nodes = boolvar(shape=n)

# Model setup
model = Model()

# Constraint 1: independent set
# No edge may have both endpoints selected.
for i, neighbors in enumerate(adjacency_list):
    for neighbor in neighbors:
        j = neighbor - 1
        if i < j:  # avoid duplicate constraints
            model += nodes[i] + nodes[j] <= 1

# Constraint 2: maximality
# Every node is either selected, or has at least one selected neighbor.
for i, neighbors in enumerate(adjacency_list):
    model += nodes[i] | any(nodes[neighbor - 1] for neighbor in neighbors)

# Solve
model.solve()

# Print the solution
solution = {"nodes": nodes.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
