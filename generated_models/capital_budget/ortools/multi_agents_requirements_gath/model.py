# Stockco – maximise NPV of a set of candidate investments subject to cash budget
# -----------------------------------------------------------------------------
# This script builds and solves a small 0/1-knapsack model with Google OR-Tools
# CP-SAT.  It prints the chosen investment pattern in JSON format with the key
# "x", exactly as required by the specification.

from ortools.sat.python import cp_model
import json

# -------------------------------------------------
# Immutable input data (exactly as given/described)
# -------------------------------------------------
npv = [16_000, 22_000, 12_000, 8_000]   # Net present value for investments 1–4
cost = [5_000, 7_000, 4_000, 3_000]      # Immediate cash outflow for each
budget = 14_000                         # Total cash available now
n = len(npv)                            # Number of candidate investments (4)

# ----------------------------
# Model, variables, constraint
# ----------------------------
model = cp_model.CpModel()

# Binary decision variables: x[i] == 1 if investment i is selected
x = [model.NewBoolVar(f"x_{i}") for i in range(n)]

# Budget (cash-outflow) constraint
model.Add(sum(cost[i] * x[i] for i in range(n)) <= budget)

# Objective: maximise total NPV
model.Maximize(sum(npv[i] * x[i] for i in range(n)))

# -------------
# Solve model
# -------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# ----------------------
# Extract and print JSON
# ----------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution = [int(solver.Value(x[i])) for i in range(n)]
else:
    # No feasible solution found (should not occur with given data).
    solution = [0] * n

print(json.dumps({"x": solution}))
