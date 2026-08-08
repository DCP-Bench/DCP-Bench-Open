
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
    [0, 0, 0,  6, 0, 8,  0, 0, 0]]
# End of data

# Model definition
model = cp.Model()

# Decision Variables: 9x9 grid with values 1..9
grid = cp.intvar(1, 9, shape=(9, 9), name="grid")

# Constraints
# Fill in the given cells
for i in range(9):
    for j in range(9):
        if input_grid[i][j] != 0:
            model += (grid[i, j] == int(input_grid[i][j]))

# Rows and columns must have all different values
for i in range(9):
    model += cp.AllDifferent(*[grid[i, j] for j in range(9)])  # row i
for j in range(9):
    model += cp.AllDifferent(*[grid[i, j] for i in range(9)])  # column j

# 3x3 blocks must have all different values
for bi in range(3):
    for bj in range(3):
        block_vars = []
        for di in range(3):
            for dj in range(3):
                block_vars.append(grid[3*bi + di, 3*bj + dj])
        model += cp.AllDifferent(*block_vars)

# Solve and print
if model.solve():
    solution = {'grid': grid.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
