from cpmpy import *
import json

# Input data
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

# Parameters
rows = len(game_data)
cols = len(game_data[0])

# Decision variables
mines = boolvar(shape=(rows, cols), name="mines")

# Model
model = Model()

# For each cell that is opened (not X), the number of adjacent mines must match the value
for i in range(rows):
    for j in range(cols):
        if game_data[i][j] != X:
            # Collect all adjacent cells (8 directions)
            adjacent_mines = []
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue  # Skip the cell itself
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols:
                        adjacent_mines.append(mines[ni, nj])
            model += [sum(adjacent_mines) == game_data[i][j]]

# Solve the model
model.solve()

# Print the solution
solution = {"mines": mines.value().tolist()}
print(json.dumps(solution))