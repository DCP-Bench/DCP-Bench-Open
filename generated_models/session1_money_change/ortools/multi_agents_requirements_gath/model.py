# -------------------------------------------------------------
# Google OR-Tools CP-SAT model for the "Alice change" problem
# -------------------------------------------------------------
# Objective  : Minimise total number of coins
# Constraints: (1) Exact change = 199 €
#              (2) Do not exceed available coins of each type
#              (3) Non-negative integral decision variables
# -------------------------------------------------------------

from ortools.sat.python import cp_model
import json

# ----------------------
# Immutable input data
# ----------------------
coin_values = [1, 2, 5, 10, 25, 50]          # v_i
available_counts = [20, 10, 15, 8, 4, 2]     # a_i
change_amount = 199                           # C
n = len(coin_values)

# ----------------------
# Model definition
# ----------------------
model = cp_model.CpModel()

# Decision variables: coin_counts[i] = number of coins of type i to give
coin_counts = [model.NewIntVar(0, available_counts[i], f"coin_{i}")
               for i in range(n)]

# Constraint 1: exact change
model.Add(sum(coin_values[i] * coin_counts[i] for i in range(n)) == change_amount)

# Constraint 2 (implicit): availability already enforced via variable bounds

# Objective: minimise total number of coins used
model.Minimize(sum(coin_counts))

# ----------------------
# Solve
# ----------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10.0  # optional time limit
status = solver.Solve(model)

# ----------------------
# Extract and print solution
# ----------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    result = {
        "coin_counts": [int(solver.Value(var)) for var in coin_counts]
    }
else:
    # If no solution exists, return zeros (still respecting output spec)
    result = {"coin_counts": [0] * n}

print(json.dumps(result))
