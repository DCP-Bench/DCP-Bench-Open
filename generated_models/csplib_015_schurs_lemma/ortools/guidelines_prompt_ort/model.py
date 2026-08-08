
from ortools.sat.python import cp_model
import json

# Input data
n = 13  # Number of balls
c = 3   # Number of boxes

# Model definition
model = cp_model.CpModel()

# Decision Variables: M[i][j] is True if ball i+1 is in box j+1
M = []
for i in range(n):
    row = []
    for j in range(c):
        var = model.NewBoolVar(f"M_{i+1}_{j+1}")
        row.append(var)
    M.append(row)

# Constraints
# 1) Each ball must be in exactly one box
for i in range(n):
    model.Add(sum(M[i][j] for j in range(c)) == 1)

# 2) For each triple (x, y, z) with x + y = z, they cannot all be in the same box
for x in range(1, n+1):
    for y in range(1, n+1):
        z = x + y
        if z <= n:
            for j in range(c):
                # M_xj + M_yj + M_zj <= 2
                model.Add(M[x-1][j] + M[y-1][j] + M[z-1][j] <= 2)

# No objective function (feasibility problem)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    balls = []
    # Determine box assignment for each ball
    for i in range(n):
        for j in range(c):
            if solver.Value(M[i][j]) == 1:
                balls.append(j+1)
                break
    solution = {
        'balls': balls
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
