# Import libraries
from cpmpy import *
import json

# Parameters
n = 8  # number of nodes in the graph
adjacency_list = [  # adjacency list for each node in the graph
    [2, 3, 7],
    [1, 4, 8],
    [1, 4, 5],
    [2, 3, 6],
    [3, 6, 7],
    [4, 5, 8],
    [1, 5, 8],
    [2, 6, 7]
]

# Decision Variables
nodes = boolvar(shape=n, name="nodes")  # Whether each node is in the maximal independent set

# Model
model = Model()

# Constraint: No two adjacent nodes can both be in the set
for i in range(n):
    for neighbor in adjacency_list[i]:
        neighbor_idx = neighbor - 1  # Convert from 1-based to 0-based indexing
        model += ~(nodes[i] & nodes[neighbor_idx])

# Objective: Maximize the size of the independent set
model.maximize(sum(nodes))

# Solve
model.solve()

# Print solution
solution = {
    "nodes": [bool(val) for val in nodes.value()]
}
print(json.dumps(solution))
# End of CPMPy script