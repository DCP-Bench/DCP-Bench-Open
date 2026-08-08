from ortools.sat.python import cp_model
import json

# Input data
n = 8  # number of nodes in the graph
adjacency_list = [  # adjacency list for each node in the graph (1-based indexing)
    [2, 3, 7],
    [1, 4, 8],
    [1, 4, 5],
    [2, 3, 6],
    [3, 6, 7],
    [4, 5, 8],
    [1, 5, 8],
    [2, 6, 7]
]

# Model definition
model = cp_model.CpModel()

# Decision Variables
# nodes[i] = 1 if node i+1 is included in the maximal independent set, else 0
nodes = [model.NewBoolVar(f'nodes_{i+1}') for i in range(n)]

# Constraints
# 1. Independent set: no two adjacent nodes can both be in the set
for i in range(n):
    for neighbor in adjacency_list[i]:
        # Convert 1-based neighbor to 0-based index
        j = neighbor - 1
        # Add constraint nodes[i] + nodes[j] <= 1 to ensure no adjacency in the set
        if i < j:  # to avoid duplicate constraints for undirected edges
            model.Add(nodes[i] + nodes[j] <= 1)

# 2. Maximality: For every node not in the set, at least one of its neighbors must be in the set
for i in range(n):
    # If node i is not in the set, then at least one neighbor is in the set
    # This can be expressed as: nodes[i] + sum of neighbors >= 1
    neighbors = [nodes[neighbor - 1] for neighbor in adjacency_list[i]]
    model.AddBoolOr(neighbors + [nodes[i].Not()])

# Objective: No objective needed, just find any feasible maximal independent set

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'nodes': [solver.Value(node) for node in nodes]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")