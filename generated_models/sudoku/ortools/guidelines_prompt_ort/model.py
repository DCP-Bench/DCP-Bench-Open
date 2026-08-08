
from ortools.sat.python import cp_model
import json

# Input data
input_grid = [  # 0 represents empty cells
    [0, 0, 0,  2, 0, 5,  0, 0, 0],
    [0, 9, 0,  0, 0, 0,  7, 3, 0],
    [0, 0, 2,  0, 0, 9,  0, 6, 0],
    [2, 0, 0,  0, 0, 0,  4, 0, 9],
    [0, 0, 0,  0, 7, 0,  0, 0, 0],
    [6, 0, 9,  0, 0, 0,  0, 0, 1],
    [0, 8, 0,  4, 0, 0,  1, 0, 0],
    [0, 6, 3,  0, 0, 0,  0, 8, 0],
    [0, 0, 0,  6, 0, 8,  0, 0, 0]
]

# Create the model
model = cp_model.CpModel()

# Decision variables: grid[i][j] in 1..9 or fixed if input != 0
grid = []
for i in range(9):
    row = []
    for j in range(9):
        if input_grid[i][j] == 0:
            var = model.NewIntVar(1, 9, f'grid_{i}_{j}')
        else:
            # Fix pre-filled cells
            var = model.NewIntVar(input_grid[i][j], input_grid[i][j], f'grid_{i}_{j}')
        row.append(var)
    grid.append(row)

# Row constraints: all digits in each row must be different
for i in range(9):
    model.AddAllDifferent(grid[i])

# Column constraints: all digits in each column must be different
for j in range(9):
    model.AddAllDifferent([grid[i][j] for i in range(9)])

# 3x3 block constraints
for bi in range(3):
    for bj in range(3):
        block = []
        for di in range(3):
            for dj in range(3):
                block.append(grid[3*bi + di][3*bj + dj])
        model.AddAllDifferent(block)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'grid': [[solver.Value(grid[i][j]) for j in range(9)] for i in range(9)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
