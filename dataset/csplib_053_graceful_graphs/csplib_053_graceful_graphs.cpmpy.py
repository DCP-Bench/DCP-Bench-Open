#!/usr/bin/python3
# Category: csplib
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/csplib/prob053_gracefull_graphs.py
# Source description: https://www.csplib.org/Problems/prob053/

# Data
m = 16  # Number of edges in the graph
n = 8  # Number of nodes in the graph
graph = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3],
         [4, 5], [4, 6], [4, 7], [5, 6], [5, 7], [6, 7],
         [0, 4], [1, 5], [2, 6], [3, 7]]  # Edges of the graph
# End of data

# Import libraries
import json
from cpmpy import *
import numpy as np


def graceful_graphs(m, n, graph):
    graph = np.array(graph)

    model = Model()

    # variables
    nodes = intvar(0, m, shape=n, name="nodes")
    edges = intvar(1, m, shape=m, name="edges")

    # constraints
    model += np.abs(nodes[graph[:, 0]] - nodes[graph[:, 1]]) == edges

    model += (AllDifferent(edges))
    model += (AllDifferent(nodes))

    return model, (nodes, edges)


# Example usage
model, (nodes, edges) = graceful_graphs(m, n, graph)
model.solve()

# Print
solution = {"nodes": nodes.value().tolist(), "edges": edges.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script
