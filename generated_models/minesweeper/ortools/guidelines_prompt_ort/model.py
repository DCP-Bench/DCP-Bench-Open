
from ortools.sat.python import cp_model
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

# Model definition
model = cp_model.CpModel()
rows = len(game_data)
cols = len(game_data[0])

# Decision variables: mines[i][j] == 1 if there's a mine at (i, j), else 0
mines = [
    [model.NewBoolVar(f"m_{i}_{j}") for j in range(cols)]
    for i in range(rows)
]

# Constraints
for i in range(rows):
    for j in range(cols):
        if game_data[i][j] == X:
            # Unopened cell: can be mine or not (no direct constraint here)
            continue
        # Opened cell: cannot be a mine
        model.Add(mines[i][j] == 0)
        # Sum of adjacent mines equals the clue number
        neighbors = []
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                ni, nj = i + di, j + dj
                if 0 <= ni < rows and 0 <= nj < cols and not (di == 0 and dj == 0):
                    neighbors.append(mines[ni][nj])
        model.Add(sum(neighbors) == game_data[i][j])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        "mines": [
            [solver.Value(mines[i][j]) for j in range(cols)]
            for i in range(rows)
        ]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
