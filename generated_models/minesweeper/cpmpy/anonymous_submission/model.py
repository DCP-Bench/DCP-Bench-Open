from cpmpy import *
import json

# Parameters
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

# Decision Variables
# Create a grid of boolean variables indicating if a cell is a mine
mines = boolvar(shape=(len(game_data), len(game_data[0])), name="mines")

# Model
model = Model()

# Constraints
for i in range(len(game_data)):
    for j in range(len(game_data[i])):
        if game_data[i][j] != X:
            # Revealed cells cannot be mines
            model += (mines[i][j] == False)
            # Count adjacent mines (8 directions)
            adjacent = []
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue  # skip current cell
                    ni, nj = i + di, j + dj
                    if 0 <= ni < len(game_data) and 0 <= nj < len(game_data[0]):
                        adjacent.append(mines[ni][nj])
            # Number of adjacent mines must match the clue
            model += (sum(adjacent) == game_data[i][j])

# Solve
model.solve()

# Output boolean values directly
solution = {
    "mines": mines.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script