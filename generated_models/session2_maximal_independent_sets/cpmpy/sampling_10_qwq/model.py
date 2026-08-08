
import cpmpy as cp
import json

n = 8
adjacency_list = [
    [2, 3, 7],   # Node 1's neighbors
    [1, 4, 8],   # Node 2's neighbors
    [1, 4, 5],   # Node 3's neighbors
    [2, 3, 6],   # Node 4's neighbors
    [3, 6, 7],   # Node 5's neighbors
    [4, 5, 8],   # Node 6's neighbors
    [1, 5, 8],   # Node 7's neighbors
    [2, 6, 7]    # Node 8's neighbors
]

model = cp.Model()

# Decision variables: nodes[i] is 1 if the (i+1)th node is included
nodes = cp.boolvar(shape=n, name="nodes")

# Independent set constraints: no two adjacent nodes are both selected
for i in range(n):
    for neighbor in adjacency_list[i]:
        j = neighbor - 1  # Convert to 0-based index
        model += nodes[i] + nodes[j] <= 1

# Maximal independent set constraints: every excluded node has a neighbor in the set
for i in range(n):
    neighbors = [(neighbor - 1) for neighbor in adjacency_list[i]]
    # nodes[i] OR any neighbor is selected
    model += nodes[i] | cp.any([nodes[j] for j in neighbors])

# Solve and print the solution
if model.solve():
    solution = {'nodes': [int(v) for v in nodes.value()]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
