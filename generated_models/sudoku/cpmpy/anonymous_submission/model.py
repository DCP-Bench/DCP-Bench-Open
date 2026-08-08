# Import libraries
from cpmpy import *
import json
import numpy as np

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

# Decision Variables
grid = intvar(1, 9, shape=(9,9), name="grid")

# Model
model = Model()

# Constraint: Fill in the given numbers
for i in range(9):
    for j in range(9):
        if input_grid[i][j] != 0:
            model += grid[i,j] == input_grid[i][j]

# Constraint: All numbers in each row must be different
for i in range(9):
    model += AllDifferent(grid[i,:])

# Constraint: All numbers in each column must be different
for j in range(9):
    model += AllDifferent(grid[:,j])

# Constraint: All numbers in each 3x3 subgrid must be different
for i in range(0,9,3):
    for j in range(0,9,3):
        model += AllDifferent(grid[i:i+3, j:j+3].flatten())

# Solve
model.solve()

# Print solution
solution = {"grid": np.array(grid.value()).tolist()}
print(json.dumps(solution))
# End of CPMPy script