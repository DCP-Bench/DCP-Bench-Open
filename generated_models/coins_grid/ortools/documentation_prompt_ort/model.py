from ortools.sat.python import cp_model
import json

# Problem parameters
n = 31  # size of the grid (31x31)
coins_per_line = 14  # coins per row and per column

# Model definition
model = cp_model.CpModel()

# Decision variables: x[i][j] = 1 if coin placed at row i, column j; 0 otherwise
x = []
for i in range(n):
    row = []
    for j in range(n):
        row.append(model.NewIntVar(0, 1, f'x_{i}_{j}'))
    x.append(row)

# Constraints
# 1. Each row must have exactly 14 coins
for i in range(n):
    model.Add(sum(x[i][j] for j in range(n)) == coins_per_line)

# 2. Each column must have exactly 14 coins
for j in range(n):
    model.Add(sum(x[i][j] for i in range(n)) == coins_per_line)

# Objective: minimize sum of squared horizontal distances from main diagonal
# distance for cell (i,j) is (i - j)^2 if coin is placed
objective_terms = []
for i in range(n):
    for j in range(n):
        dist_sq = (i - j) * (i - j)
        # Add dist_sq * x[i][j] to objective
        # Since x[i][j] is 0/1, this is linear
        objective_terms.append(dist_sq * x[i][j])

model.Minimize(sum(objective_terms))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Extract solution for x as list of lists of 0/1
    x_sol = []
    for i in range(n):
        row_sol = []
        for j in range(n):
            row_sol.append(solver.Value(x[i][j]))
        x_sol.append(row_sol)
    # Calculate the sum of quadratic horizontal distances from main diagonal
    z = 0
    for i in range(n):
        for j in range(n):
            if solver.Value(x[i][j]) == 1:
                z += (i - j) * (i - j)
    solution = {
        'x': x_sol,
        'z': z
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")