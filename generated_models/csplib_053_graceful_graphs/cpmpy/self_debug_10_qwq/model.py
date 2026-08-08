
import cpmpy as cp
import json

m = 16
n = 8
graph = [
    [0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3],
    [4, 5], [4, 6], [4, 7], [5, 6], [5, 7], [6, 7],
    [0, 4], [1, 5], [2, 6], [3, 7]
]

model = cp.Model()

# Decision Variables
nodes = cp.intvar(0, m, shape=n, name="nodes")

# Constraints
model += cp.AllDifferent(nodes)

edge_diffs = []
for u, v in graph:
    diff = cp.abs(nodes[u] - nodes[v])
    edge_diffs.append(diff)
model += cp.AllDifferent(edge_diffs)

# Solve and print
if model.solve():
    solution = {
        'nodes': nodes.value().tolist(),
        'edges': [int(d.value()) for d in edge_diffs]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
