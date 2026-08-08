#!/usr/bin/env python3
"""Clock face rearrangement under triplet-sum ≤ 21

This script uses Google OR-Tools CP-SAT solver to place the numbers 1..12 around a
circular clock so that the sum of every three consecutive numbers does not exceed
21.  The first position (12 o’clock) is fixed to the number 12 as required by the
problem statement.  A single feasible arrangement is returned as JSON with key
'x'.
"""

import json
from ortools.sat.python import cp_model

# -----------------------------
# 0. Input data (fixed / none)
# -----------------------------
# The problem statement contains no run-time input; all data are constants.
N = 12  # number of positions / numbers
MAX_TRIPLET_SUM = 21
numbers = list(range(1, N + 1))

# -----------------------------
# 1. Model
# -----------------------------
model = cp_model.CpModel()

# 1.1 Decision variables: x[p] is the integer placed at position p (0..11)
# domain 1..12 inclusive
x = [model.NewIntVar(1, N, f"x[{p}]") for p in range(N)]

# 1.2 All-different (permutation) constraint
model.AddAllDifferent(x)

# 1.3 Fix first position to 12
model.Add(x[0] == 12)

# 1.4 Triplet-sum constraint with wrap-around
for p in range(N):
    model.Add(x[p] + x[(p + 1) % N] + x[(p + 2) % N] <= MAX_TRIPLET_SUM)

# No optimisation objective – pure feasibility

# -----------------------------
# 2. Solve
# -----------------------------
solver = cp_model.CpSolver()
# Optional: small time limit to avoid runaway in pathological cases
solver.parameters.max_time_in_seconds = 30.0
status = solver.Solve(model)

# -----------------------------
# 3. Output
# -----------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution = [solver.Value(var) for var in x]
    print(json.dumps({"x": solution}))
else:
    # Per specification we should always be able to find a solution; if not, raise.
    raise RuntimeError("No feasible arrangement found under given constraints.")
