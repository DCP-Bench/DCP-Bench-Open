from ortools.sat.python import cp_model
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

rows = len(game_data)
cols = len(game_data[0])

# Model definition
model = cp_model.CpModel()

# Decision Variables
# mines[r][c] = 1 if cell (r,c) is a mine, 0 otherwise
mines = []
for r in range(rows):
    row_vars = []
    for c in range(cols):
        if game_data[r][c] == X:
            # Unknown cell, can be mine or not
            var = model.NewIntVar(0, 1, f'mine_{r}_{c}')
        else:
            # Known cell, cannot be mine
            var = model.NewIntVar(0, 0, f'mine_{r}_{c}')
        row_vars.append(var)
    mines.append(row_vars)

# Constraints
# For each cell with a number (0-8), the sum of mines in adjacent cells must equal that number
for r in range(rows):
    for c in range(cols):
        if game_data[r][c] != X:
            # Collect neighbors
            neighbors = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if not (nr == r and nc == c):
                            neighbors.append(mines[nr][nc])
            # Sum of mines around must be equal to the clue number
            model.Add(sum(neighbors) == game_data[r][c])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'mines': [[solver.Value(mines[r][c]) for c in range(cols)] for r in range(rows)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")