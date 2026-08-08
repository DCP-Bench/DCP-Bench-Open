# -------------------------------------------------------------
# Costas Array Construction (n = 8) using Google OR-Tools CP-SAT
# -------------------------------------------------------------
# 1. Fully self-contained: just run the script.
# 2. Reads the fixed input data exactly as specified, nothing else.
# 3. Builds a CP model that implements *all* CAP constraints.
# 4. Solves for one feasible Costas permutation and prints it as JSON.
# -------------------------------------------------------------

import json
from ortools.sat.python import cp_model

# -------------------------------------------------------------
# Input data (immutable as provided)
# -------------------------------------------------------------
n = 8  # Size of the Costas array

# -------------------------------------------------------------
# CP-SAT model
# -------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables: costas[i] = column position of the mark in row i (1-based).
# Domain: 1..n.  AllDifferent enforces permutation property.
costas = [model.NewIntVar(1, n, f"x_{i}") for i in range(n)]
model.AddAllDifferent(costas)

# Difference triangle variables
y_vars = {}  # key = (l, i) ➜ y_{l,i}
for l in range(1, n):
    current_row = []
    for i in range(n - l):
        y = model.NewIntVar(-(n - 1), n - 1, f"y_{l}_{i}")
        # Definition: y = costas[i] − costas[i+l]
        model.Add(y == costas[i] - costas[i + l])
        # Zero can never appear (because permutation implies costas[i] ≠ costas[i+l])
        model.Add(y != 0)
        y_vars[(l, i)] = y
        current_row.append(y)
    # All differences in the same lag line must be unique.
    model.AddAllDifferent(current_row)

# -------------------------------------------------------------
# Solve
# -------------------------------------------------------------
solver = cp_model.CpSolver()
# A time limit can be added if desired, e.g. solver.parameters.max_time_in_seconds = 30
status = solver.Solve(model)

# -------------------------------------------------------------
# Output (JSON with key 'costas' exactly)
# -------------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution = [solver.Value(v) for v in costas]
    print(json.dumps({"costas": solution}))
else:
    # If no solution is found (theoretically impossible for n=8), output empty list.
    print(json.dumps({"costas": []}))
