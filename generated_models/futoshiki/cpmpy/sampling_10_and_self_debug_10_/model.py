
import cpmpy as cp
import json

# Data
values = [[0, 0, 3, 2, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0]]

# 1-based inequalities: [i1,j1, i2,j2] means cell(i1,j1) < cell(i2,j2)
lt = [[1, 2, 1, 1], [1, 4, 1, 5], [2, 3, 1, 3], [3, 3, 2, 3], [3, 4, 2, 4],
      [2, 5, 3, 5], [3, 2, 4, 2], [4, 4, 4, 3], [5, 2, 5, 1], [5, 4, 5, 3],
      [5, 5, 4, 5]]
# End of data

# Model definition
model = cp.Model()

# Decision Variables: 5x5 grid with values 1..5
grid = cp.intvar(1, 5, shape=(5, 5), name="grid")

# Constraints

# Given values
for i in range(5):
    for j in range(5):
        if values[i][j] != 0:
            model += (grid[i, j] == values[i][j])

# AllDifferent for each row
for r in range(5):
    model += cp.AllDifferent(grid[r, :])

# AllDifferent for each column
for c in range(5):
    model += cp.AllDifferent(grid[:, c])

# Inequality constraints (convert 1-based to 0-based)
for a, b, c_, d in lt:
    i1 = a - 1; j1 = b - 1
    i2 = c_ - 1; j2 = d - 1
    model += (grid[i1, j1] < grid[i2, j2])

# Solve and print
if model.solve():
    solution = {'grid': grid.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
