from cpmpy import *
import json

# Input data
n = 8  # number of nodes in the graph
adjacency_list = [
    [2, 3, 7],
    [1, 4, 8],
    [1, 4, 5],
    [2, 3, 6],
    [3, 6, 7],
    [4, 5, 8],
    [1, 5, 8],
    [2, 6, 7]
]

# Adjust to 0-based indexing
adjacency_list = [[x - 1 for x in lst] for lst in adjacency_list]

# Decision variables
nodes = boolvar(shape=n, name="nodes")

# Model
model = Model()

# No two adjacent nodes can both be in the independent set
for i in range(n):
    for j in adjacency_list[i]:
        model += [nodes[i] + nodes[j] <= 1]

# Maximal independent set: for every node not in the set, at least one of its neighbors is in the set
for i in range(n):
    model += [nodes[i] | (sum(nodes[j] for j in adjacency_list[i]) >= 1)]

# Solve the model
model.solve()

# Print the solution
solution = {"nodes": nodes.value().tolist()}
print(json.dumps(solution))