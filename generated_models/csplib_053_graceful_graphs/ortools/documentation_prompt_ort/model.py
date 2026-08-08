from ortools.sat.python import cp_model
import json

# Input data
m = 16  # Number of edges in the graph
n = 8   # Number of nodes in the graph
graph = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3],
         [4, 5], [4, 6], [4, 7], [5, 6], [5, 7], [6, 7],
         [0, 4], [1, 5], [2, 6], [3, 7]]  # Edges of the graph

# Model definition
model = cp_model.CpModel()

# Decision Variables
# nodes[i] is the label assigned to node i, in [0..m]
nodes = [model.NewIntVar(0, m, f'nodes_{i}') for i in range(n)]

# edges[i] is the label assigned to edge i, which is the absolute difference of the labels of its nodes
edges = [model.NewIntVar(1, m, f'edges_{i}') for i in range(m)]

# Constraints

# All node labels are distinct
model.AddAllDifferent(nodes)

# All edge labels are distinct
model.AddAllDifferent(edges)

# Edge label is the absolute difference of the node labels it connects
for i, (u, v) in enumerate(graph):
    diff = model.NewIntVar(0, m, f'diff_{i}')
    model.Add(diff == nodes[u] - nodes[v]).OnlyEnforceIf()
    # Use absolute value constraint
    model.AddAbsEquality(edges[i], nodes[u] - nodes[v])

# Objective: None (just find a feasible graceful labeling)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'nodes': [solver.Value(node) for node in nodes],
        'edges': [solver.Value(edge) for edge in edges]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")