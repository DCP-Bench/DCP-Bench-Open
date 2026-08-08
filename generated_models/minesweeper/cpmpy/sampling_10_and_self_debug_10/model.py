
import cpmpy as cp
import json

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

rows = len(game_data)
cols = len(game_data[0])

# Decision variables: mines[i][j] = 1 if cell (i,j) is a mine, 0 otherwise
mines = cp.intvar(0, 1, shape=(rows, cols), name="mines")

model = cp.Model()

# Constraint: cells that are opened and have a number (0-8) must have that many mines around
for i in range(rows):
    for j in range(cols):
        if game_data[i][j] != X:
            # Collect neighbors coordinates
            neighbors = []
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols:
                        if not (ni == i and nj == j):
                            neighbors.append(mines[ni, nj])
            # Sum of mines around must equal the clue number
            model += cp.sum(neighbors) == game_data[i][j]

# Constraint: cells that are opened and have a number cannot be mines themselves
for i in range(rows):
    for j in range(cols):
        if game_data[i][j] != X:
            model += mines[i, j] == 0

# Solve and print
if model.solve():
    solution = {'mines': mines.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
