# Complete, runnable Python program that uses OR-Tools CP-SAT to find three
# numbers from a fixed list that sum to zero and prints the chosen indices
# as a JSON object.

import json
from ortools.sat.python import cp_model

# --------------------------- Input Data -----------------------------------
nums = [-1, 6, 8, 9, 10, -100, 78, 0, 1]  # Collection of integers (immutable)
# --------------------------------------------------------------------------

# ------------------------ Model Construction ------------------------------
model = cp_model.CpModel()

n = len(nums)
# Decision variables: indices[i] == 1 if element i is selected, else 0
indices = [model.NewBoolVar(f"idx_{i}") for i in range(n)]

# Constraint 1: Exactly three elements must be selected
model.Add(sum(indices) == 3)

# Constraint 2: Selected elements must sum to zero
model.Add(sum(nums[i] * indices[i] for i in range(n)) == 0)

# No objective function is required (pure feasibility problem)

# --------------------------- Solve Model ----------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# ------------------------- Extract Solution -------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution_indices = [int(solver.Value(var)) for var in indices]
else:
    # No feasible solution found; return all zeros for completeness
    solution_indices = [0] * n

# ------------------------- Output Result ----------------------------------
print(json.dumps({"indices": solution_indices}))
