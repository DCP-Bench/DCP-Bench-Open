from cpmpy import *
import json

# Parameters
m = 16  # Number of edges in the graph
n = 8  # Number of nodes in the graph
graph = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3],
         [4, 5], [4, 6], [4, 7], [5, 6], [5, 7], [6, 7],
         [0, 4], [1, 5], [2, 6], [3, 7]]  # Edges of the graph

# Decision variables
nodes = intvar(0, m, shape=n, name="nodes")
edges = intvar(1, m, shape=m, name="edges")

# Model
model = Model()

# All node labels are unique
model += [AllDifferent(nodes)]

# All edge labels are unique
model += [AllDifferent(edges)]

# For each edge, the label is the absolute difference of the node labels
for i in range(m):
    u, v = graph[i]
    model += [abs(nodes[u] - nodes[v]) == edges[i]]

# Ensure that the edge labels are exactly the values from 1 to m
model += [edges == arange(1, m + 1)]

# Solve the model
model.solve()

# Print the solution
solution = {"nodes": nodes.value().tolist(), "edges": edges.value().tolist()}
print(json.dumps(solution))