import json
from ortools.sat.python import cp_model

# ---------------------------
# Data parsing (no external input for this puzzle)
# ---------------------------
# The set of positions is fixed and implicitly defined by the layout.
# There are exactly eight positions indexed 1..8.

# ---------------------------
# CP-SAT model construction
# ---------------------------
model = cp_model.CpModel()

# Decision variables: digit placed at each position (1..8)
positions = [model.NewIntVar(1, 8, f"pos_{i}") for i in range(1, 9)]

# 1. All digits must be different
model.AddAllDifferent(positions)

# Convenience aliases that match the mathematical description
# Indexing in the requirement starts at 1, Python list starts at 0
p1, p2, p3, p4, p5, p6, p7, p8 = positions

# 2. Square-sum constraints
model.Add(p2 == p1 + p3)  # square at position 2
model.Add(p4 == p1 + p6)  # square at position 4
model.Add(p5 == p3 + p8)  # square at position 5
model.Add(p7 == p6 + p8)  # square at position 7

# ---------------------------
# Solve
# ---------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10  # small safety limit
status = solver.Solve(model)

# ---------------------------
# Output
# ---------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution = [solver.Value(var) for var in positions]
    print(json.dumps({"positions": solution}))
else:
    # If no solution exists, still provide valid JSON (could also raise)
    print(json.dumps({"positions": []}))
