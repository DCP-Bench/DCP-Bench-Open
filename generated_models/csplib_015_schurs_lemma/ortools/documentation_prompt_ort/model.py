from ortools.sat.python import cp_model
import json

# Input data
n = 13  # Number of balls
c = 3   # Number of boxes

# Model definition
model = cp_model.CpModel()

# Decision Variables
# M[i][j] = 1 if ball i+1 is in box j+1, else 0
M = []
for i in range(n):
    row = []
    for j in range(c):
        row.append(model.NewBoolVar(f'M_{i+1}_{j+1}'))
    M.append(row)

# Constraints
# Each ball must be in exactly one box
for i in range(n):
    model.Add(sum(M[i][j] for j in range(c)) == 1)

# For each triple (x,y,z) with x + y = z, and for each box j,
# not all three balls are in the same box
# i.e. M[xj] + M[yj] + M[zj] <= 2
for z in range(1, n+1):
    for x in range(1, z):
        y = z - x
        if y >= 1 and y <= n and y <= x:  # To avoid duplicates, enforce y <= x
            for j in range(c):
                model.Add(M[x-1][j] + M[y-1][j] + M[z-1][j] <= 2)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    balls = [0] * n
    for i in range(n):
        for j in range(c):
            if solver.Value(M[i][j]) == 1:
                balls[i] = j + 1
                break
    solution = {'balls': balls}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")