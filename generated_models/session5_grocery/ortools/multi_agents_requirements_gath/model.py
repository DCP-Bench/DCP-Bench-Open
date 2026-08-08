#!/usr/bin/env python3
"""Solve the classical 7.11 grocery-store puzzle with Google OR-Tools (CP-SAT).

The four unknown item prices (in cents) must satisfy two simultaneous
conditions:
  • Their sum is 711¢.
  • Their product is 711 000 000 (which equals 7.11 dollars when converted
    back from cents).

The script builds a small CP model, solves it, and prints the four prices as
JSON – exactly in the key “prices”, as required.
"""
import json
from ortools.sat.python import cp_model

# -------------------------
# 1. Parse (empty) input.
#    The problem instance is fixed, so no actual parsing is required – but we
#    keep this section to respect the specification.
# -------------------------
# (Nothing to parse – instance is hard-coded.)

# -------------------------
# 2. Build the CP-SAT model.
# -------------------------
model = cp_model.CpModel()

NUM_ITEMS = 4
TOTAL_SUM_CENTS = 711              # 7.11 USD expressed in cents
TOTAL_PROD_CENTS4 = 711_000_000    # 7.11 * 100⁴ (product in “cent⁴”)

# Decision variables: price of each item in whole cents (positive integers)
prices = [model.NewIntVar(1, TOTAL_SUM_CENTS, f"price_{i}")
          for i in range(NUM_ITEMS)]

# Optional symmetry-breaking: enforce non-decreasing order
for i in range(NUM_ITEMS - 1):
    model.Add(prices[i] <= prices[i + 1])

# Sum constraint
model.Add(sum(prices) == TOTAL_SUM_CENTS)

# Product constraint.
# CP-SAT offers AddMultiplicationEquality, which works for two factors.
# We chain two-factor products through auxiliary variables so that the final
# product equals the required constant.
prod01 = model.NewIntVar(1, TOTAL_PROD_CENTS4, "prod01")
model.AddMultiplicationEquality(prod01, [prices[0], prices[1]])

prod012 = model.NewIntVar(1, TOTAL_PROD_CENTS4, "prod012")
model.AddMultiplicationEquality(prod012, [prod01, prices[2]])

# Final product – fixed to the known constant
final_product = model.NewIntVar(TOTAL_PROD_CENTS4, TOTAL_PROD_CENTS4,
                               "final_product")
model.AddMultiplicationEquality(final_product, [prod012, prices[3]])

# Pure feasibility problem – no objective needed.

# -------------------------
# 3. Invoke the solver.
# -------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# -------------------------
# 4. Output result as required JSON.
# -------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    result = {"prices": [solver.Value(p) for p in prices]}
else:
    # No solution found – return empty list to satisfy strict JSON schema.
    result = {"prices": []}

print(json.dumps(result))