# Import libraries
from cpmpy import *
import json

# Parameters
m = 16  # Number of edges in the graph
n = 8  # Number of nodes in the graph
graph = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3],
         [4, 5], [4, 6], [4, 7], [5, 6], [5, 7], [6, 7],
         [0, 4], [1, 5], [2, 6], [3, 7]]  # Edges of the graph

# Decision Variables
nodes = intvar(0, m, shape=n, name="nodes")  # Node labels (0 to q where q=m edges)
edges = intvar(1, m, shape=m, name="edges")  # Edge labels (1 to q where q=m edges)

# Model
model = Model()

# Constraint: all node labels are unique and in 0..m
model += AllDifferent(nodes)

# Constraint: edge labels are all different and in 1..m
model += AllDifferent(edges)

# Constraint: edge labels are absolute differences of node labels
for i, (u, v) in enumerate(graph):
    model += edges[i] == abs(nodes[u] - nodes[v])

# Additional constraint to ensure edge labels cover 1..m exactly
# This is already implied by AllDifferent(edges) and the range of edges,
# but we add it for clarity
model += [edges[i] >= 1 for i in range(m)]
model += [edges[i] <= m for i in range(m)]

# Solve
model.solve()

# Print solution
solution = {
    "nodes": nodes.value().tolist(),
    "edges": edges.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script