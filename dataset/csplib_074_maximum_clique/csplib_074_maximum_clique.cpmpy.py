#!/usr/bin/python3
# Category: csplib
# Source: https://www.csplib.org/Problems/prob074/
# Source model: https://www.csplib.org/Problems/prob074/models/Clique.py.html

"""
Given a simple undirected graph G = (V, E), a clique is a subset of vertices V
where every two distinct vertices in the subset are adjacent (connected by an edge).
The maximum clique problem is to find a clique of the largest possible size in a given graph.

Print a binary array (c) of n elements indicating which vertices are included in the maximum clique, where
c[i] is 1 if vertex i is in the clique, 0 otherwise.
"""

# Data
# The number of vertices in the graph.
n = 5
# The adjacency matrix of the graph. adj[i][j] is 1 if there's an edge.
adj = [[0, 1, 0, 1, 0],
       [1, 0, 1, 0, 0],
       [0, 1, 0, 1, 1],
       [1, 0, 1, 0, 1],
       [0, 0, 1, 1, 0]]
# End of data

# Import libraries
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# c[i] is 1 if vertex i is in the clique, 0 otherwise.
c = cp.boolvar(shape=n, name="c")

# Constraints
# The clique property must hold: if two vertices i and j are not connected,
# they cannot both be in the clique.
for i in range(n):
    for j in range(i + 1, n):  # Iterate over unique pairs of vertices
        if adj[i][j] == 0:
            # At most one of the two non-adjacent vertices can be in the clique.
            model += c[i] + c[j] <= 1

# Objective: Maximize the size of the clique.
# The size is the total number of vertices selected.
model.maximize(cp.sum(c))

# Solve and print
if model.solve():
    solution = {"c": c.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")