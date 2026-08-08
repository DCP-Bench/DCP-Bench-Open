import json
from ortools.sat.python import cp_model

# ------------ Data ----------------------------------------------------------
# 1-U devices
devices = ["A", "B", "C", "D", "E", "F", "G", "H"]
num_slots = len(devices)  # 8
slots = range(1, num_slots + 1)  # 1..8 inclusive

# Number of cables between unordered device pairs
cables = {
    ("A", "H"): 1,
    ("A", "E"): 2,
    ("B", "F"): 4,
    ("C", "G"): 1,
    ("C", "D"): 1,
    ("C", "E"): 1,
    ("D", "H"): 3,
    ("G", "H"): 1,
}

# Ensure symmetry in the dictionary for convenience
def _key(u, v):
    return (u, v) if (u, v) in cables else (v, u)

# ------------ Model ---------------------------------------------------------
model = cp_model.CpModel()

# Position variables: one per device, domain 1..8
pos = {
    d: model.NewIntVar(1, num_slots, f"pos_{d}") for d in devices
}

# All devices must occupy distinct slots
model.AddAllDifferent(pos.values())

# Distance variables for each linked pair and weighted contribution
weighted_terms = []  # list of weighted distance IntVars to sum later

for (u, v), k in cables.items():
    # Absolute distance |pos_u - pos_v|
    dist = model.NewIntVar(0, num_slots - 1, f"dist_{u}_{v}")
    model.AddAbsEquality(dist, pos[u] - pos[v])
    if k == 1:
        # weight == 1 → no need for new variable, use dist directly
        weighted_terms.append(dist)
    else:
        # Multiply distance by k via a new variable
        w_dist = model.NewIntVar(0, k * (num_slots - 1), f"w{u}_{v}")
        model.AddMultiplicationEquality(w_dist, [dist, k])
        weighted_terms.append(w_dist)

# Total cable length
max_total = sum(k for k in cables.values()) * (num_slots - 1)
final_sum = model.NewIntVar(0, max_total, "final_sum")
model.Add(final_sum == sum(weighted_terms))

# Objective: minimise total cable length
model.Minimize(final_sum)

# ------------ Solve ---------------------------------------------------------
solver = cp_model.CpSolver()
# Optional: enable more search effort (not strictly required)
solver.parameters.max_time_in_seconds = 10.0
status = solver.Solve(model)

# ------------ Output --------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    result = {
        "final_sum": solver.Value(final_sum)
    }
    print(json.dumps(result))
else:
    # Should not happen for this small instance, but keep graceful degradation
    print(json.dumps({"final_sum": None}))
