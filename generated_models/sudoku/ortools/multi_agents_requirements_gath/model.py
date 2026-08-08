import json
from ortools.sat.python import cp_model

# ------------------------------
# 1. Input data (immutable)
# ------------------------------
input_grid = [  # 0 represents empty cells
    [0, 0, 0,  2, 0, 5,  0, 0, 0],
    [0, 9, 0,  0, 0, 0,  7, 3, 0],
    [0, 0, 2,  0, 0, 9,  0, 6, 0],

    [2, 0, 0,  0, 0, 0,  4, 0, 9],
    [0, 0, 0,  0, 7, 0,  0, 0, 0],
    [6, 0, 9,  0, 0, 0,  0, 0, 1],

    [0, 8, 0,  4, 0, 0,  1, 0, 0],
    [0, 6, 3,  0, 0, 0,  0, 8, 0],
    [0, 0, 0,  6, 0, 8,  0, 0, 0]
]

# ------------------------------
# 2. Model
# ------------------------------
model = cp_model.CpModel()

# Decision variables: grid[r][c] ∈ {1,..,9}
grid = []
for r in range(9):
    row = []
    for c in range(9):
        # Variable name helps debugging but is optional
        var = model.NewIntVar(1, 9, f"g_{r}_{c}")
        row.append(var)
    grid.append(row)

# ------------------------------
# 3. Constraints
# ------------------------------
# 3.1 Preset numbers (clues)
for r in range(9):
    for c in range(9):
        if input_grid[r][c] != 0:
            model.Add(grid[r][c] == input_grid[r][c])

# 3.2 Row uniqueness
for r in range(9):
    model.AddAllDifferent(grid[r])

# 3.3 Column uniqueness
for c in range(9):
    col_vars = [grid[r][c] for r in range(9)]
    model.AddAllDifferent(col_vars)

# 3.4 3x3 Block uniqueness
for br in range(0, 9, 3):
    for bc in range(0, 9, 3):
        block_vars = [grid[r][c]
                      for r in range(br, br + 3)
                      for c in range(bc, bc + 3)]
        model.AddAllDifferent(block_vars)

# No objective function – feasibility problem

# ------------------------------
# 4. Solve
# ------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30  # optional limit
status = solver.Solve(model)

# ------------------------------
# 5. Output
# ------------------------------
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solved_grid = [[int(solver.Value(grid[r][c])) for c in range(9)] for r in range(9)]
    print(json.dumps({"grid": solved_grid}))
else:
    # If somehow no solution exists (shouldn't happen for valid Sudoku), still output JSON.
    print(json.dumps({"grid": None}))
