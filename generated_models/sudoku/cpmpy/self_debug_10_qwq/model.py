
import cpmpy as cp
import json

input_grid = [
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

model = cp.Model()

# Decision variables
grid = cp.intvar(1, 9, shape=(9, 9), name="grid")

# Constraints for initial values
for i in range(9):
    for j in range(9):
        if input_grid[i][j] != 0:
            model += (grid[i, j] == input_grid[i][j])

# Row constraints
for i in range(9):
    model += cp.AllDifferent(grid[i, :])

# Column constraints
for j in range(9):
    model += cp.AllDifferent(grid[:, j])

# Subgrid constraints
for block_row in [0, 3, 6]:
    for block_col in [0, 3, 6]:
        subgrid = grid[block_row:block_row+3, block_col:block_col+3].flatten()
        model += cp.AllDifferent(subgrid)

# Solve and print
if model.solve():
    solution = {'grid': grid.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
