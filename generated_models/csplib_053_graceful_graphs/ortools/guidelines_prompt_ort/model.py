
from ortools.sat.python import cp_model
import json

# Input data
m = 16  # Number of edges
n = 8   # Number of nodes
graph = [
    [0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3],
    [4, 5], [4, 6], [4, 7], [5, 6], [5, 7], [6, 7],
    [0, 4], [1, 5], [2, 6], [3, 7]
]

# Create the CP-SAT model
model = cp_model.CpModel()

# Decision variables for node labels: each node gets a unique label in 0..m
nodes = [model.NewIntVar(0, m, f"nodes[{i}]") for i in range(n)]
model.AddAllDifferent(nodes)

# (Optional) symmetry breaking: fix the label of node 0 to 0
model.Add(nodes[0] == 0)

# Decision variables for edge labels: each edge label = |difference of its nodes|
edges = []
for idx, (u, v) in enumerate(graph):
    e = model.NewIntVar(1, m, f"edges[{idx}]")
    # Absolute difference constraint
    model.AddAbsEquality(e, nodes[u] - nodes[v])
    edges.append(e)

# All edge labels must be different
model.AddAllDifferent(edges)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'nodes': [solver.Value(nodes[i]) for i in range(n)],
        'edges': [solver.Value(edges[i]) for i in range(m)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
