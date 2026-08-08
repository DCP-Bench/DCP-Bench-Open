
import cpmpy as cp
import json

# Data
n = 8  # number of nodes in the graph
adjacency_list = [  # adjacency list for each node (1-based node ids in the data)
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

# Decision Variables: boolean for each node, 1 means the node is in the independent set
nodes = cp.boolvar(shape=n, name="nodes")

# Constraints

# 1) Independent set: no two adjacent nodes can both be selected.
# Add each undirected edge only once.
seen_edges = set()
for i in range(n):
    for j_1based in adjacency_list[i]:
        j = j_1based - 1  # convert to 0-based index
        if i == j:
            continue
        edge = tuple(sorted((i, j)))
        if edge in seen_edges:
            continue
        seen_edges.add(edge)
        model += (nodes[i] + nodes[j] <= 1)

# 2) Maximality: every node not selected must have at least one neighbor selected.
for i in range(n):
    neigh_indices = [j_1based - 1 for j_1based in adjacency_list[i]]
    # If there are no neighbors (isolated node), for maximality it must be selected.
    if len(neigh_indices) == 0:
        model += (nodes[i] == 1)
    else:
        model += (~nodes[i]).implies(cp.sum([nodes[j] for j in neigh_indices]) >= 1)

# Solve and print
if model.solve():
    # convert boolean list to 0/1 integers
    nodes_list = [int(v) for v in nodes.value().tolist()]
    solution = {'nodes': nodes_list}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
