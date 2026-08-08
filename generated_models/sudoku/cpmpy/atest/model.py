from cpmpy import *
import json

# Input data
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

# Parameters
n = 9  # Size of the grid

# Decision variables
grid = intvar(1, n, shape=(n, n), name="grid")

# Model
model = Model()

# Fill in the initial values from the input grid
for i in range(n):
    for j in range(n):
        if input_grid[i][j] != 0:
            model += [grid[i, j] == input_grid[i][j]]

# Each row must contain all digits from 1 to 9
for i in range(n):
    model += [AllDifferent(grid[i, :])]

# Each column must contain all digits from 1 to 9
for j in range(n):
    model += [AllDifferent(grid[:, j])]

# Each 3x3 subgrid must contain all digits from 1 to 9
for block_row in range(0, n, 3):
    for block_col in range(0, n, 3):
        subgrid = []
        for i in range(3):
            for j in range(3):
                subgrid.append(grid[block_row + i, block_col + j])
        model += [AllDifferent(subgrid)]

# Solve the model
model.solve()

# Print the solution
solution = {"grid": grid.value().tolist()}
print(json.dumps(solution))