
from ortools.sat.python import cp_model
import json

# Input data
n = 8  # number of nodes in the graph
adjacency_list = [
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

# Decision Variables: nodes[i] = 1 if node i is in the independent set, else 0
nodes = [model.NewBoolVar(f'n{i}') for i in range(n)]

# Constraints
# 1. No two adjacent nodes can both be in the independent set
for i in range(n):
    for j in adjacency_list[i]:
        # adjacency_list uses 1-based node numbering
        j_idx = j - 1
        # Add constraint nodes[i] + nodes[j_idx] <= 1
        model.Add(nodes[i] + nodes[j_idx] <= 1)

# 2. Maximality: for each node i, either it is in the set, or at least one neighbor is
for i in range(n):
    neighbor_vars = [nodes[j - 1] for j in adjacency_list[i]]
    # nodes[i] + sum(neighbors) >= 1 ensures you can't add i if it's not present
    model.Add(nodes[i] + sum(neighbor_vars) >= 1)

# Objective: maximize the size of the independent set (this also yields a maximal one)
model.Maximize(sum(nodes))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'nodes': [solver.Value(nodes[i]) for i in range(n)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
