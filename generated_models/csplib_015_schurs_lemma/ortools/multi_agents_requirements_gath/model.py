import json
from ortools.sat.python import cp_model

# --------------------------------------------------
# Input data (immutable, must not be changed)
# --------------------------------------------------
n = 13  # Number of balls
c = 3   # Number of boxes (labelled 1..3)

# --------------------------------------------------
# Model creation
# --------------------------------------------------
model = cp_model.CpModel()

# Binary placement variables M_{i,j} == 1  <=>  ball i (1..n) is put into box j (1..c)
M = {}
for i in range(n):
    for j in range(c):
        M[i, j] = model.NewBoolVar(f"M_{i+1}_{j+1}")

# 1. Each ball must be placed in exactly one box
for i in range(n):
    model.Add(sum(M[i, j] for j in range(c)) == 1)

# 2. For every additive triple (x, y, z) with x + y = z and z <= n,
#    forbid that all three balls sit in the same box.
for x in range(1, n + 1):
    for y in range(x + 1, n + 1):  # ensure x < y
        z = x + y
        if z <= n:
            for j in range(c):
                # M_{xj} + M_{yj} + M_{zj} <= 2  (cannot all be 1)
                model.Add(M[x - 1, j] + M[y - 1, j] + M[z - 1, j] <= 2)

# --------------------------------------------------
# Solve
# --------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

balls = []  # the required output list
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    # Translate binary matrix back into a single integer per ball (1..3)
    for i in range(n):
        for j in range(c):
            if solver.Value(M[i, j]):
                balls.append(j + 1)  # j is 0-based internally
                break
else:
    # The theoretical model says n < 14 always feasible, but guard anyway
    raise ValueError("No feasible assignment found for the given parameters.")

# --------------------------------------------------
# Output exactly as requested (JSON with key 'balls')
# --------------------------------------------------
print(json.dumps({"balls": balls}))
