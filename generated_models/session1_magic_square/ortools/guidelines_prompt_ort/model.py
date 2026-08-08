
from ortools.sat.python import cp_model
import json

# Size of the magic square
n = 4
magic_sum = n * (n * n + 1) // 2  # Magic constant

# Create the model
model = cp_model.CpModel()

# Decision variables: square[i][j] in 1..n^2
square = [
    [model.NewIntVar(1, n * n, f'square[{i}][{j}]') for j in range(n)]
    for i in range(n)
]

# All cells must take different values
model.AddAllDifferent(sum(square, []))

# Row sum constraints
for i in range(n):
    model.Add(sum(square[i][j] for j in range(n)) == magic_sum)

# Column sum constraints
for j in range(n):
    model.Add(sum(square[i][j] for i in range(n)) == magic_sum)

# Diagonal sum constraints
model.Add(sum(square[i][i] for i in range(n)) == magic_sum)
model.Add(sum(square[i][n - 1 - i] for i in range(n)) == magic_sum)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution as JSON
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'square': [
            [solver.Value(square[i][j]) for j in range(n)]
            for i in range(n)
        ]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
