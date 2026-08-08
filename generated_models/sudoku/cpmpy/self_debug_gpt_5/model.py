
import cpmpy as cp
import json

# Data (optional)
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

# Decision Variables
grid = cp.intvar(1, 9, shape=(9, 9), name="grid")

# Constraints
# Prefilled cells
for i in range(9):
    for j in range(9):
        if input_grid[i][j] != 0:
            model += (grid[i, j] == input_grid[i][j])

# Rows and columns must be all-different
for i in range(9):
    model += cp.AllDifferent(grid[i, :])
for j in range(9):
    model += cp.AllDifferent(grid[:, j])

# 3x3 subgrids must be all-different
for bi in range(0, 9, 3):
    for bj in range(0, 9, 3):
        cells = [grid[bi + di, bj + dj] for di in range(3) for dj in range(3)]
        model += cp.AllDifferent(cells)

# Solve and print
if model.solve():
    solution = {'grid': grid.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
