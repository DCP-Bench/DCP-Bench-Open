
import cpmpy as cp
import json

# Data
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
# End of data

# Model definition
model = cp.Model()

# Decision Variables: a 9x9 grid with values from 1 to 9
grid = cp.intvar(1, 9, shape=(9, 9), name="grid")

# Constraints

# 1) Pre-filled cells
for i in range(9):
    for j in range(9):
        if input_grid[i][j] != 0:
            model += (grid[i, j] == input_grid[i][j])

# 2) All rows must contain different digits
for i in range(9):
    model += cp.all_different(grid[i, :])

# 3) All columns must contain different digits
for j in range(9):
    model += cp.all_different(grid[:, j])

# 4) All 3x3 sub-grids must contain different digits
for bi in range(0, 9, 3):
    for bj in range(0, 9, 3):
        block = [grid[bi + di, bj + dj] for di in range(3) for dj in range(3)]
        model += cp.all_different(block)

# Solve and print
if model.solve():
    solution = {'grid': grid.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
