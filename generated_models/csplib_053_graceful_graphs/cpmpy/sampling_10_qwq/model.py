
import cpmpy as cp
import json

m = 16  # Number of edges
n = 8   # Number of nodes
graph = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3],
         [4, 5], [4, 6], [4, 7], [5, 6], [5, 7], [6, 7],
         [0, 4], [1, 5], [2, 6], [3, 7]]

model = cp.Model()

# Decision variables: node labels from 0 to m (16)
nodes = cp.intvar(0, m, shape=n, name="nodes")

# Constraints
# All nodes must have unique labels
model += cp.AllDifferent(nodes)

# Compute edge labels as absolute differences of their nodes
edge_labels = []
for u, v in graph:
    edge_labels.append(cp.abs(nodes[u] - nodes[v]))

# All edge labels must be distinct
model += cp.AllDifferent(edge_labels)

# Solve
if model.solve():
    # Extract solution values
    solution_nodes = nodes.value().tolist()
    # Compute edge labels based on node values
    solution_edges = []
    for u, v in graph:
        solution_edges.append(abs(solution_nodes[u] - solution_nodes[v]))
    solution = {'nodes': solution_nodes, 'edges': solution_edges}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
