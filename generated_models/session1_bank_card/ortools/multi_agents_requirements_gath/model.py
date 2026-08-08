#!/usr/bin/env python3
"""Solve the 4-digit PIN puzzle with Google OR-Tools CP-SAT.

The PIN consists of four different non-zero decimal digits (a,b,c,d) that satisfy
 1) The two–digit number cd is three times the two–digit number ab.
 2) The two–digit number da is two times the two–digit number bc.

The script finds one feasible assignment and prints the digits as JSON with the
required key order ['b', 'd', 'c', 'a'].
"""

import json
from ortools.sat.python import cp_model

# ----------------------------
# Model definition
# ----------------------------
model = cp_model.CpModel()

# Decision variables: digits 1..9 (no zeros allowed)
a = model.NewIntVar(1, 9, "a")
b = model.NewIntVar(1, 9, "b")
c = model.NewIntVar(1, 9, "c")
d = model.NewIntVar(1, 9, "d")

# All-different constraint
model.AddAllDifferent([a, b, c, d])

# cd = 3 * ab   -> 10*c + d = 3*(10*a + b)
model.Add(10 * c + d == 3 * (10 * a + b))

# da = 2 * bc   -> 10*d + a = 2*(10*b + c)
model.Add(10 * d + a == 2 * (10 * b + c))

# ----------------------------
# Solve
# ----------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# ----------------------------
# Output
# ----------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    result = {
        "b": solver.Value(b),
        "d": solver.Value(d),
        "c": solver.Value(c),
        "a": solver.Value(a),
    }
else:
    # No solution found – return empty JSON as a safeguard.
    result = {}

print(json.dumps(result))
