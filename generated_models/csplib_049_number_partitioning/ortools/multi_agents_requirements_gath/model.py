#!/usr/bin/env python3
"""Partition 1..n into two equal‐size subsets with equal sums and equal square sums.
   Feasibility modelled with Google OR-Tools CP-SAT.
"""
import json
from ortools.sat.python import cp_model

# ---------------------
# Input data (immutable)
# ---------------------
n = 12  # The number N

# -------------------------------------------------
# Quick pre-check: necessary arithmetic feasibility
# -------------------------------------------------
if n < 8 or n % 4 != 0:
    # Problem is provably infeasible, print empty solution structure.
    print(json.dumps({"A": [], "B": []}))
    exit(0)

# ----------------------
# Derived constant terms
# ----------------------
cardinality   = n // 2                              # |A| = |B|
subset_sum    = n * (n + 1) // 4                    # Required sum of elements in A
subset_sq_sum = n * (n + 1) * (2 * n + 1) // 12     # Required sum of squares in A

# ----------------------------
# Build CP-SAT feasibility model
# ----------------------------
model = cp_model.CpModel()

# Decision variables: x_i = 1 if i belongs to subset A, else 0 (which means it belongs to B).
x = [model.NewBoolVar(f"x_{i}") for i in range(1, n + 1)]

# Constraint 1: correct cardinality
model.Add(sum(x) == cardinality)

# Constraint 2: equal sum of elements
model.Add(sum(i * x[i - 1] for i in range(1, n + 1)) == subset_sum)

# Constraint 3: equal sum of squares of elements
model.Add(sum((i * i) * x[i - 1] for i in range(1, n + 1)) == subset_sq_sum)

# ----------------------------
# Solve the model (pure feasibility)
# ----------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10  # small instance; keep a safety cap
status = solver.Solve(model)

# ----------------------------
# Extract and print the result
# ----------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    A = [i for i in range(1, n + 1) if solver.BooleanValue(x[i - 1])]
    B = [i for i in range(1, n + 1) if not solver.BooleanValue(x[i - 1])]
    print(json.dumps({"A": A, "B": B}))
else:
    # No feasible partition found (should not happen for valid n >= 8 divisible by 4)
    print(json.dumps({"A": [], "B": []}))
