import json
from ortools.sat.python import cp_model

# -----------------------------
# Input data (immutable)
# -----------------------------
demands = [4, 8, 10, 7, 12, 4]  # Demand for buses in each 4-hour slot
n_slots = len(demands)          # Number of 4-hour intervals (6)
shift_len = 2                   # Each bus covers 2 consecutive slots (8 hours)

# -----------------------------
# Model creation
# -----------------------------
model = cp_model.CpModel()

# Decision variables: x[i] = buses starting in slot i
# Upper bound: worst case each bus serves only one demand unit
upper_bound = sum(demands)
x = [model.NewIntVar(0, upper_bound, f"x[{i}]") for i in range(n_slots)]

# -----------------------------
# Constraints
# -----------------------------
for i in range(n_slots):
    # Coverage: buses starting in current or previous slot must meet demand
    prev = (i - 1) % n_slots
    model.Add(x[i] + x[prev] >= demands[i])

# -----------------------------
# Objective: minimise total fleet size
# -----------------------------
model.Minimize(sum(x))

# -----------------------------
# Solve the model
# -----------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10  # small timeout safeguard
status = solver.Solve(model)

# -----------------------------
# Output processing
# -----------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    result = {"x": [int(solver.Value(var)) for var in x]}
    print(json.dumps(result))
else:
    # If no solution, return empty allocation (per spec we must print JSON)
    print(json.dumps({"x": []}))
