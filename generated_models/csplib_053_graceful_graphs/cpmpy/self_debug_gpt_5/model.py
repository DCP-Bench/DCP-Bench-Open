
import cpmpy as cp
import json

# Data (optional)
m = 16  # Number of edges in the graph
n = 8   # Number of nodes in the graph
graph = [
    [0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3],
    [4, 5], [4, 6], [4, 7], [5, 6], [5, 7], [6, 7],
    [0, 4], [1, 5], [2, 6], [3, 7]
]  # Edges of the graph
# End of data

# Model definition
model = cp.Model()

# Decision Variables
nodes = cp.intvar(0, m, shape=n, name="nodes")
edges = cp.intvar(1, m, shape=m, name="edges")

# Constraints
# All node labels are distinct and within 0..m
model += cp.AllDifferent(nodes)

# Each edge label equals the absolute difference of its endpoints
for i, (u, v) in enumerate(graph):
    model += (edges[i] == cp.Abs(nodes[u] - nodes[v]))

# All edge labels are distinct (thus a permutation of 1..m)
model += cp.AllDifferent(edges)

# Optional but safe symmetry-breaking: graceful labelings always use 0 and m
model += (cp.Minimum(nodes) == 0)
model += (cp.Maximum(nodes) == m)

# Objective (none, satisfaction problem)

# Solve and print
if model.solve():
    solution = {
        'nodes': nodes.value().tolist(),
        'edges': edges.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
