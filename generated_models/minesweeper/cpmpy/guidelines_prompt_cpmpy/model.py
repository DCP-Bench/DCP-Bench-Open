
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
# End of data

# Model definition
model = cp.Model()

# Dimensions
n_rows = len(game_data)
n_cols = len(game_data[0])

# Decision Variables: whether each cell is a mine (1) or not (0)
mines = cp.intvar(0, 1, shape=(n_rows, n_cols), name="mines")

# Constraints
for i in range(n_rows):
    for j in range(n_cols):
        if game_data[i][j] >= 0:
            # Open cell: no mine here
            model += (mines[i, j] == 0)
            # Sum of adjacent mines equals the clue
            neighbors = []
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < n_rows and 0 <= nj < n_cols:
                        neighbors.append(mines[ni, nj])
            model += (cp.sum(neighbors) == game_data[i][j])

# Solve
if model.solve():
    # Extract solution and convert to pure Python ints
    mines_solution = [
        [int(val) for val in row]
        for row in mines.value().tolist()
    ]
    solution = {'mines': mines_solution}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
