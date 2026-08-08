"""Graceful labelling for a fixed 8-node, 16-edge graph
====================================================
Find a graceful labelling (Gallian, All-Interval variant) with Google OR-Tools
CP-SAT.  The script prints the node labels and edge labels as JSON with the
exact keys ['edges', 'nodes'] demanded by the evaluation harness.
"""

# 1. Imports -----------------------------------------------------------
from ortools.sat.python import cp_model
import json

# 2. Immutable input data ---------------------------------------------
m = 16  # number of edges
n = 8   # number of nodes

graph = [
    [0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3],  # K4 on {0,1,2,3}
    [4, 5], [4, 6], [4, 7], [5, 6], [5, 7], [6, 7],  # K4 on {4,5,6,7}
    [0, 4], [1, 5], [2, 6], [3, 7]                   # perfect matching
]  # |graph| = 16 = m

# 3. CP-SAT model ------------------------------------------------------
model = cp_model.CpModel()

# Decision variables (order matters – first *edges*, then *nodes*)
edges = [model.NewIntVar(1, m, f"edge_{e}") for e in range(m)]  # 1..16, all-different
nodes = [model.NewIntVar(0, m, f"node_{i}") for i in range(n)]  # 0..16, all-different

# Injective labels
model.AddAllDifferent(edges)
model.AddAllDifferent(nodes)

# Edge definition: absolute difference of endpoint labels
for e, (u, v) in enumerate(graph):
    model.AddAbsEquality(edges[e], nodes[u] - nodes[v])

# No objective – pure feasibility

# 4. Configure solver --------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.num_search_workers = 8  # use all available cores when possible
# Optional time limit (comment out if you prefer an exhaustive search)
# solver.parameters.max_time_in_seconds = 60

# 5. Solve -------------------------------------------------------------
status = solver.Solve(model)

# 6. Output ------------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    edge_labels = [solver.Value(v) for v in edges]  # length 16
    node_labels = [solver.Value(v) for v in nodes]  # length 8
    print(json.dumps({"edges": edge_labels, "nodes": node_labels}))
else:
    # No solution found (within limits) – still emit JSON with correct keys
    print(json.dumps({"edges": [], "nodes": []}))
