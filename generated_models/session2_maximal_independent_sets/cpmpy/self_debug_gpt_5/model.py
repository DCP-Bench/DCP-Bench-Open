
import cpmpy as cp
import json

# Data (optional)
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

# Convert adjacency list to 0-based indices
adjacency_0 = [[v - 1 for v in neigh] for neigh in adjacency_list]

# Model definition
model = cp.Model()

# Decision Variables
nodes = cp.boolvar(shape=n, name="nodes")  # 1 if node is in the independent set, else 0

# Constraints

# Independent set: no two adjacent nodes can both be selected
for i in range(n):
    for j in adjacency_0[i]:
        if j > i:  # enforce each undirected edge once
            model += (cp.sum([nodes[i], nodes[j]]) <= 1)

# Maximality: for every node not in the set, at least one neighbor must be in the set
for i in range(n):
    neigh = adjacency_0[i]
    if len(neigh) == 0:
        # Isolated node must be included to be maximal
        model += (nodes[i] == 1)
    else:
        model += (nodes[i] | (cp.sum([nodes[j] for j in neigh]) >= 1))

# Objective (none, any maximal independent set is fine)

# Solve and print
if model.solve():
    solution = {'nodes': [int(v) for v in nodes.value().tolist()]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
