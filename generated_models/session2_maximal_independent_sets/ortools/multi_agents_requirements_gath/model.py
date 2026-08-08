# Maximal Independent Set with Google OR-Tools (CP-SAT)
# ------------------------------------------------------
# This script builds a feasibility model that finds any
# maximal independent set for the fixed, undirected graph
# described by the hard-coded adjacency list.
# The result is printed as a JSON object with a single key
# "nodes", whose value is a 0/1 list indicating whether each
# corresponding vertex is in the chosen maximal independent set.

from ortools.sat.python import cp_model
import json

# ------------------------------------------------------------------
# 1. Input data (fixed / hard coded)
# ------------------------------------------------------------------

n = 8  # number of vertices
adjacency_list = [  # 1-based vertex indices inside the lists
    [2, 3, 7],
    [1, 4, 8],
    [1, 4, 5],
    [2, 3, 6],
    [3, 6, 7],
    [4, 5, 8],
    [1, 5, 8],
    [2, 6, 7]
]

# ------------------------------------------------------------------
# 2. Model definition
# ------------------------------------------------------------------

model = cp_model.CpModel()

# Decision variables: nodes[i] == 1  <=> vertex (i+1) is selected.
nodes = [model.NewBoolVar(f"v_{i+1}") for i in range(n)]

# ------------------------------------------------------------------
# 3. Independence constraints: no two adjacent vertices both chosen.
# ------------------------------------------------------------------

for i in range(n):
    for j in adjacency_list[i]:
        j_idx = j - 1  # convert to 0-based index
        # Add each undirected edge only once (i < j_idx) to avoid duplicates.
        if i < j_idx:
            model.Add(nodes[i] + nodes[j_idx] <= 1)

# ------------------------------------------------------------------
# 4. Maximality constraints: for every vertex either it or one of its
#    neighbors must be in the set (cannot extend the solution).
# ------------------------------------------------------------------

for i in range(n):
    neighbor_vars = [nodes[j - 1] for j in adjacency_list[i]]
    model.Add(nodes[i] + sum(neighbor_vars) >= 1)

# No objective is needed (pure feasibility).

# ------------------------------------------------------------------
# 5. Solve the model
# ------------------------------------------------------------------

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise ValueError("No maximal independent set found (model is infeasible).")

# ------------------------------------------------------------------
# 6. Extract solution
# ------------------------------------------------------------------

solution_nodes = [int(solver.Value(var)) for var in nodes]

# ------------------------------------------------------------------
# 7. Output results as JSON (exact required key set)
# ------------------------------------------------------------------

print(json.dumps({"nodes": solution_nodes}))
