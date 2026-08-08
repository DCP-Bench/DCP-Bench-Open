import json
from ortools.sat.python import cp_model

# ---------------------------
# Input data (immutable)
# ---------------------------
target = 20  # Target number of beers
pack_sizes = [7, 13]

# ---------------------------
# CP-SAT model construction
# ---------------------------
model = cp_model.CpModel()

# A generous upper bound on how many packs of any size could ever be needed.
# In the worst case we buy only the smallest pack; add the target itself as
# extra slack to ensure the domain is always large enough.
max_packs_needed = (target // min(pack_sizes)) + target

# Decision variables: how many packs of each size to buy
x = [model.NewIntVar(0, max_packs_needed, f"x_{s}") for s in pack_sizes]

# Linear expression for the total number of beers purchased
total_beers = sum(s * var for s, var in zip(pack_sizes, x))

# ---------------------------
# Constraints
# ---------------------------
# C2 – satisfy or exceed the requested amount
model.Add(total_beers >= target)

# ---------------------------
# Objective (O1 – minimise surplus)
# ---------------------------
model.Minimize(total_beers - target)

# ---------------------------
# Solve
# ---------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# ---------------------------
# Output (JSON with key 'counts')
# ---------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    counts = [solver.Value(var) for var in x]
    print(json.dumps({"counts": counts}))
else:
    raise RuntimeError("No feasible solution found.")
