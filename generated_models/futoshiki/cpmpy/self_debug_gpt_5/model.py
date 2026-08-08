
import cpmpy as cp
import json

# Data (optional)
values = [
    [0, 0, 3, 2, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

# [i1,j1, i2,j2] requires that values[i1,j1] < values[i2,j2], 1-based indices
lt = [
    [1, 2, 1, 1], [1, 4, 1, 5], [2, 3, 1, 3], [3, 3, 2, 3], [3, 4, 2, 4],
    [2, 5, 3, 5], [3, 2, 4, 2], [4, 4, 4, 3], [5, 2, 5, 1], [5, 4, 5, 3],
    [5, 5, 4, 5]
]
# End of data

n = len(values)

# Model definition
model = cp.Model()

# Decision Variables
grid = cp.intvar(1, n, shape=(n, n), name="grid")

# Constraints

# Given values
for i in range(n):
    for j in range(n):
        if values[i][j] != 0:
            model += (grid[i, j] == values[i][j])

# Row and column AllDifferent constraints (Latin square)
for i in range(n):
    model += cp.AllDifferent(grid[i, :])
for j in range(n):
    model += cp.AllDifferent(grid[:, j])

# Inequality constraints (convert 1-based to 0-based)
for (i1, j1, i2, j2) in lt:
    model += (grid[i1 - 1, j1 - 1] < grid[i2 - 1, j2 - 1])

# Solve and print
if model.solve():
    solution = {'grid': grid.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
