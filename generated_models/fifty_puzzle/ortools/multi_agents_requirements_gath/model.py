#!/usr/bin/env python3
"""Coney-Island dummy subset problem solved with Google OR-Tools CP-SAT.

A carnival booth displays 10 dummies whose printed numbers are
[15, 9, 30, 21, 19, 3, 12, 6, 25, 27].  The player wins if the sum of
numbers on the knocked-down dummies is exactly 50.  The program below
models the task as a simple feasibility problem and prints one valid
subset (if any) as JSON under the key "dummies".
"""

import json
from ortools.sat.python import cp_model

# ---------------------------------------------------------------------------
# Immutable data (problem instance)
# ---------------------------------------------------------------------------
VALUES = [15, 9, 30, 21, 19, 3, 12, 6, 25, 27]  # Numbers printed on dummies
TARGET = 50                                      # Desired exact total
NUM_DUMMIES = len(VALUES)

# ---------------------------------------------------------------------------
# Model definition
# ---------------------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables: x[i] == 1 if dummy i is knocked down, 0 otherwise
x = [model.NewBoolVar(f"x_{i}") for i in range(NUM_DUMMIES)]

# Exact-sum constraint
model.Add(sum(VALUES[i] * x[i] for i in range(NUM_DUMMIES)) == TARGET)

# No objective: pure feasibility

# ---------------------------------------------------------------------------
# Solve
# ---------------------------------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    selected = [VALUES[i] for i in range(NUM_DUMMIES) if solver.Value(x[i])]
    print(json.dumps({"dummies": selected}))
else:
    # Problem guarantees at least one solution; this branch should never execute.
    print(json.dumps({"dummies": []}))
