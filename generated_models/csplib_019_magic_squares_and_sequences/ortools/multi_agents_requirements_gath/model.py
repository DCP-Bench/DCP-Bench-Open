#!/usr/bin/env python3
"""Solve the magic-sequence problem for a fixed length n using Google OR-Tools CP-SAT.
A magic (self-describing) sequence x[0..n-1] satisfies
    – each x_i is between 0 and n-1,
    – for every value i, the number i occurs exactly x_i times in the sequence,
    – consequently, sum(x_i) = n.
The script builds a standard indicator (global-cardinality) encoding, feeds it to
CP-SAT, and prints one feasible sequence as JSON.
"""

import json
from ortools.sat.python import cp_model

# -----------------------------------------------------------------------------
# Input data (provided verbatim by the exercise specification)
# -----------------------------------------------------------------------------

n = 12  # Length of the magic sequence

# -----------------------------------------------------------------------------
# Model
# -----------------------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables: x[0..n-1]
x = [model.NewIntVar(0, n - 1, f"x_{i}") for i in range(n)]

# Indicator variables b[(j,i)] – true iff x_j == i
b = {}
for j in range(n):
    row_bools = []
    for i in range(n):
        b_var = model.NewBoolVar(f"b_{j}_{i}")
        b[(j, i)] = b_var
        # Reified equality/inequality links
        model.Add(x[j] == i).OnlyEnforceIf(b_var)
        model.Add(x[j] != i).OnlyEnforceIf(b_var.Not())
        row_bools.append(b_var)
    # Each position j takes exactly one value i
    model.AddExactlyOne(row_bools)

# Magic (self-describing) property: for each value i, count occurrences
for i in range(n):
    model.Add(sum(b[(j, i)] for j in range(n)) == x[i])

# Redundant strengthening: total length must be n
model.Add(sum(x) == n)

# -----------------------------------------------------------------------------
# Solve
# -----------------------------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10  # safeguard (instance is tiny)
solver.parameters.num_search_workers = 8    # use available cores
status = solver.Solve(model)

# -----------------------------------------------------------------------------
# Output – strictly JSON with the required key list ['x']
# -----------------------------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    result = {
        "x": [int(solver.Value(x_i)) for x_i in x]
    }
else:
    # Infeasible (should not happen for n = 12); return empty list to keep JSON schema
    result = {"x": []}

print(json.dumps(result))
