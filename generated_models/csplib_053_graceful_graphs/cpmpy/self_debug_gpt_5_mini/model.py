
import cpmpy as cp
import json

# Data
m = 16  # Number of edges
n = 8   # Number of nodes
graph = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3],
         [4, 5], [4, 6], [4, 7], [5, 6], [5, 7], [6, 7],
         [0, 4], [1, 5], [2, 6], [3, 7]]  # Edges (as pairs of node indices)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# Node labels: unique integers from 0..m
nodes = cp.intvar(0, m, shape=n, name="nodes")
# Edge labels: absolute differences, must be 1..m and all different
edges = cp.intvar(1, m, shape=m, name="edges")

# Constraints
# All node labels are distinct
model += cp.AllDifferent(nodes)
# All edge labels are distinct
model += cp.AllDifferent(edges)

# Link edges to absolute differences of node labels
for i, (u, v) in enumerate(graph):
    model += (edges[i] == cp.Abs(nodes[u] - nodes[v]))

# Symmetry breaking: fix one node to 0 (optional but helps search)
model += (nodes[0] == 0)

# Since there are m edges and edge labels are distinct in 1..m, they will form exactly the set {1..m}

# Solve and print
if model.solve():
    solution = {
        'nodes': nodes.value().tolist(),
        'edges': edges.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
