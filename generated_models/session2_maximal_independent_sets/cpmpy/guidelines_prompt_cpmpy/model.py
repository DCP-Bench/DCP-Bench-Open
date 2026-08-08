
import cpmpy as cp
import json

# Data
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
# End of data

# Model definition
model = cp.Model()

# Decision Variables: nodes[i] == 1 if node i+1 is in the independent set
nodes = cp.BoolVar(shape=n, name="nodes")

# Constraints
# 1) Independence: no two adjacent nodes both selected
for i in range(n):
    for j in adjacency_list[i]:
        # j-1 to convert 1-based neighbor index to 0-based
        model += nodes[i] + nodes[j-1] <= 1

# 2) Maximality: every node not selected must have at least one selected neighbor
for i in range(n):
    neighbor_vars = [nodes[j-1] for j in adjacency_list[i]]
    # nodes[i] + sum(neighbors) >= 1 ensures that if nodes[i]==0, some neighbor is 1
    model += nodes[i] + cp.sum(neighbor_vars) >= 1

# Solve
if model.solve():
    # Convert boolean array to list of 0/1 integers
    nodes_sol = [int(v) for v in nodes.value().tolist()]
    solution = {"nodes": nodes_sol}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
