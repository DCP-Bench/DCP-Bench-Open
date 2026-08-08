
import cpmpy as cp
import json

# Input data
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

n = len(game_data)
m = len(game_data[0])

# Model definition
model = cp.Model()

# Decision Variables: mines[i,j] = 1 if there is a mine, 0 otherwise
mines = cp.intvar(0, 1, shape=(n, m), name="mines")

# Constraints:
# - If a cell is opened (0-8), it cannot be a mine.
# - For each opened cell with value v, the sum of neighboring mines must equal v.
for i in range(n):
    for j in range(m):
        val = game_data[i][j]
        if val != X:
            # cell is opened, no mine here
            model += (mines[i, j] == 0)
            # collect neighbors
            nbrs = []
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    ni = i + di
                    nj = j + dj
                    if 0 <= ni < n and 0 <= nj < m:
                        if not (ni == i and nj == j):
                            nbrs.append(mines[ni, nj])
            model += (cp.sum(nbrs) == int(val))

# Solve and print
if model.solve():
    solution = {'mines': mines.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
