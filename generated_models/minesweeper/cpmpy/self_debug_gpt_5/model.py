
import cpmpy as cp
import json
import numpy as np

# Data (optional)
X = -1
game_data = [  # 0-8: number of mines around, -1: not opened
    [2, 3, X, 2, 2, X, 2, 1],
    [X, X, 4, X, X, 4, X, 2],
    [X, X, X, X, X, X, 4, X],
    [X, 5, X, 6, X, X, X, 2],
    [2, X, X, X, 5, 5, X, 2],
    [1, 3, 4, X, X, X, 4, X],
    [0, 1, X, 4, X, X, X, 3],
    [0, 1, 2, X, 2, 3, X, 2]
]
# End of data

# Model definition
model = cp.Model()

rows = len(game_data)
cols = len(game_data[0])

# Decision Variables
# mines[i,j] = 1 if there is a mine at (i,j), 0 otherwise
mines = cp.intvar(0, 1, shape=(rows, cols), name="mines")

# Constraints
for i in range(rows):
    for j in range(cols):
        val = game_data[i][j]
        if val >= 0:
            # Revealed numbered cells cannot be mines
            model += (mines[i, j] == 0)
            # Sum of adjacent mines equals the number shown
            neighbors = []
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols:
                        neighbors.append(mines[ni, nj])
            model += (cp.sum(neighbors) == val)

# Objective (optional)
# No objective, just find a feasible placement of mines

# Solve and print
if model.solve():
    solution = {'mines': mines.value().tolist()}
    # Ensure JSON-friendly ints (0/1)
    solution['mines'] = [[int(v) for v in row] for row in solution['mines']]
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
