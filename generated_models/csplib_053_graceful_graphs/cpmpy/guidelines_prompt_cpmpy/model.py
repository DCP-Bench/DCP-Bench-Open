
import cpmpy as cp
import json

# Data
m = 16  # Number of edges
n = 8   # Number of nodes
graph = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3],
         [4, 5], [4, 6], [4, 7], [5, 6], [5, 7], [6, 7],
         [0, 4], [1, 5], [2, 6], [3, 7]]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# nodes[i] is the label for node i, from 0..m
nodes = cp.intvar(0, m, shape=n, name="nodes")
# edges[j] is the label for edge j, from 1..m
edges = cp.intvar(1, m, shape=m, name="edges")

# Constraints
# All node labels must be different
model += cp.AllDifferent(nodes)
# All edge labels must be different
model += cp.AllDifferent(edges)
# Edge label is the absolute difference of its endpoint labels
for idx, (u, v) in enumerate(graph):
    model += edges[idx] == cp.abs(nodes[u] - nodes[v])

# Solve and print
if model.solve():
    solution = {
        "nodes": nodes.value().tolist(),
        "edges": edges.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
