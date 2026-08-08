
from ortools.sat.python import cp_model
import json

# Grid size and number of coins per row/column
n = 31
coins_per_line = 14

# Create the model
model = cp_model.CpModel()

# Decision variables: x[i][j] == 1 if there's a coin in cell (i,j), else 0
x = [
    [model.NewBoolVar(f'x_{i}_{j}') for j in range(n)]
    for i in range(n)
]

# Row constraints: exactly coins_per_line coins in each row
for i in range(n):
    model.Add(sum(x[i][j] for j in range(n)) == coins_per_line)

# Column constraints: exactly coins_per_line coins in each column
for j in range(n):
    model.Add(sum(x[i][j] for i in range(n)) == coins_per_line)

# Objective: minimize the sum of squared horizontal distances from the main diagonal
# distance = (i - j), so squared distance = (i - j)^2
model.Minimize(
    sum((i - j) * (i - j) * x[i][j]
        for i in range(n) for j in range(n))
)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x': [[solver.Value(x[i][j]) for j in range(n)] for i in range(n)],
        'z': int(solver.ObjectiveValue())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
