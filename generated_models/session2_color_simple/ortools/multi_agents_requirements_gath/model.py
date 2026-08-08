import json
from ortools.sat.python import cp_model

# --------------------------------------------------
# Input data  (do NOT modify)
# --------------------------------------------------
graph = [  # adjacency list: (i, j) means country i borders country j (1-based indices)
    [3, 1],
    [3, 6],
    [3, 4],
    [6, 4],
    [6, 1],
    [1, 5],
    [1, 4],
    [4, 5],
    [4, 2],
]

# --------------------------------------------------
# Model construction
# --------------------------------------------------
model = cp_model.CpModel()

num_countries = 6  # Belgium, Denmark, France, Germany, Netherlands, Luxembourg (in this order)
max_possible_colors = num_countries  # upper bound on number of distinct colours

# Decision variables ---------------------------------------------------------
colors = [
    model.NewIntVar(1, max_possible_colors, f"color_{i}") for i in range(num_countries)
]
# Auxiliary variable representing the highest colour index actually used
K = model.NewIntVar(1, max_possible_colors, "K")

# Constraints ---------------------------------------------------------------
# 1. Adjacent countries must get different colours
for edge in graph:
    i, j = edge  # still 1-based
    model.Add(colors[i - 1] != colors[j - 1])

# 2. Link K with colour variables so that K is at least the maximum colour used
for c in colors:
    model.Add(c <= K)

# Objective -----------------------------------------------------------------
model.Minimize(K)

# --------------------------------------------------
# Solve
# --------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution_colors = [solver.Value(var) for var in colors]
    print(json.dumps({"colors": solution_colors}))
else:
    # No solution should not happen for a proper map-colouring instance,
    # but we still guard against it.
    print(json.dumps({"colors": []}))
