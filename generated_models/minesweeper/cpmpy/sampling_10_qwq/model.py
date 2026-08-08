
import cpmpy as cp
import json

# Data
X = -1
game_data = [
    [2, 3, X, 2, 2, X, 2, 1],
    [X, X, 4, X, X, 4, X, 2],
    [X, X, X, X, X, X, 4, X],
    [X, 5, X, 6, X, X, X, 2],
    [2, X, X, X, 5, 5, X, 2],
    [1, 3, 4, X, X, X, 4, X],
    [0, 1, X, 4, X, X, X, 3],
    [0, 1, 2, X, 2, 3, X, 2]
]

# Model definition
model = cp.Model()

# Decision Variables
variables = cp.boolvar(shape=(8, 8), name="mine")

# Constraints
for i in range(8):
    for j in range(8):
        current = game_data[i][j]
        if current != X:  # Cell is a number (not X)
            # The cell itself is safe (not a mine)
            model += (variables[i, j] == 0)
            # Calculate sum of adjacent cells
            total = 0
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue  # Skip the cell itself
                    ni, nj = i + di, j + dj
                    if 0 <= ni < 8 and 0 <= nj < 8:
                        total += variables[ni, nj]
            model += (total == current)

# Solve and print
if model.solve():
    solution = {'mines': variables.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
