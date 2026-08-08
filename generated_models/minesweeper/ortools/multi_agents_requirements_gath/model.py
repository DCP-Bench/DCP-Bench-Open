import json
from ortools.sat.python import cp_model

# -------------------------------
# 1. Parse input data (immutable)
# -------------------------------
X = -1
game_data = [
    # 0-8: number of mines around, -1: not opened
    [2, 3, X, 2, 2, X, 2, 1],
    [X, X, 4, X, X, 4, X, 2],
    [X, X, X, X, X, X, 4, X],
    [X, 5, X, 6, X, X, X, 2],
    [2, X, X, X, 5, 5, X, 2],
    [1, 3, 4, X, X, X, 4, X],
    [0, 1, X, 4, X, X, X, 3],
    [0, 1, 2, X, 2, 3, X, 2],
]

ROWS = len(game_data)
COLS = len(game_data[0])

# -------------------------------
# 2. Build CP-SAT model
# -------------------------------
model = cp_model.CpModel()

# Decision variables: mines[i][j] is 1 if cell (i,j) contains a mine.
mines = [[model.NewBoolVar(f"mine_{i}_{j}") for j in range(COLS)] for i in range(ROWS)]

# Constraint C1: Numbered cells cannot be mines.
for i in range(ROWS):
    for j in range(COLS):
        if game_data[i][j] != -1:
            model.Add(mines[i][j] == 0)

# Helper to list neighbours of a cell (Moore neighbourhood).
def neighbours(r, c):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                yield nr, nc

# Constraint C2: Clue consistency.
for i in range(ROWS):
    for j in range(COLS):
        clue = game_data[i][j]
        if clue != -1:  # only apply to numbered cells
            neighbour_vars = [mines[r][c] for r, c in neighbours(i, j)]
            model.Add(sum(neighbour_vars) == clue)

# No objective (pure feasibility).

# -------------------------------
# 3. Solve
# -------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise ValueError("No feasible solution found for the given Minesweeper board.")

# -------------------------------
# 4. Extract solution
# -------------------------------
solution_mines = [[int(solver.Value(mines[i][j])) for j in range(COLS)] for i in range(ROWS)]

# -------------------------------
# 5. Output JSON
# -------------------------------
print(json.dumps({"mines": solution_mines}))
