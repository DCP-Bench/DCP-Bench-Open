
import cpmpy as cp
import json

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

# Model definition
model = cp.Model()

# Decision Variables
# nodes[i] = 1 if node i is in the maximal independent set, else 0
nodes = cp.boolvar(shape=n, name="nodes")

# Constraints
# 1) Independent set: no two adjacent nodes both included
for i in range(n):
    for j in adjacency_list[i]:
        # j is 1-based, convert to 0-based index
        model += (nodes[i] + nodes[j-1] <= 1)

# 2) Maximality: For every node not in the set, at least one neighbor is in the set
for i in range(n):
    neighbors = [nodes[j-1] for j in adjacency_list[i]]
    model += (nodes[i] + cp.sum(neighbors) >= 1)

# Objective: None (just find any maximal independent set)
# Solve and print
if model.solve():
    solution = {'nodes': [int(x) for x in nodes.value().tolist()]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
