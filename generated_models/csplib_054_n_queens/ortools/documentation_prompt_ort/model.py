from ortools.sat.python import cp_model
import json

# Input data
n = 10  # Size of the chessboard and number of queens

# Model definition
model = cp_model.CpModel()

# Decision Variables
# queens[col] = row position of the queen in column 'col'
queens = [model.NewIntVar(0, n - 1, f'queen_{col}') for col in range(n)]

# Constraints
# 1. All queens must be in different rows
model.AddAllDifferent(queens)

# 2. No two queens share the same diagonal
# For diagonals, we use the fact that queens on the same diagonal have equal (row - col) or (row + col)
diag1 = []
diag2 = []
for col in range(n):
    diag1.append(model.NewIntVar(-n, n, f'diag1_{col}'))
    diag2.append(model.NewIntVar(0, 2 * n, f'diag2_{col}'))
    model.Add(diag1[col] == queens[col] - col)
    model.Add(diag2[col] == queens[col] + col)

model.AddAllDifferent(diag1)
model.AddAllDifferent(diag2)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Extract the positions of the queens as (column, row) pairs
    # Note: columns are from 0 to n-1, rows are solver.Value(queens[col])
    solution = {
        'queens': [[col, solver.Value(queens[col])] for col in range(n)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")