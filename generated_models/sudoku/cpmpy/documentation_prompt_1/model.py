
import cpmpy as cp
import json

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

# Model definition
model = cp.Model()

# Decision Variables: 9x9 grid with values 1..9
grid = cp.intvar(1, 9, shape=(9, 9), name="grid")

# Constraints

# 1) Pre-filled cells constraints
for i in range(9):
    for j in range(9):
        if input_grid[i][j] != 0:
            model += (grid[i, j] == input_grid[i][j])

# 2) Rows have all different values
for i in range(9):
    model += cp.AllDifferent(grid[i, :])

# 3) Columns have all different values
for j in range(9):
    model += cp.AllDifferent(grid[:, j])

# 4) 3x3 subgrids have all different values
for block_i in range(3):
    for block_j in range(3):
        block = []
        for di in range(3):
            for dj in range(3):
                block.append(grid[block_i*3 + di, block_j*3 + dj])
        model += cp.AllDifferent(block)

# Solve and print
if model.solve():
    solution = {'grid': grid.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
