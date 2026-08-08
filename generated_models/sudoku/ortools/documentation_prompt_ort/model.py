from ortools.sat.python import cp_model
import json

# Input data
input_grid = [  # 0 represents empty cells
    [0, 0, 0,  2, 0, 5,  0, 0, 0],
    [0, 9, 0,  0, 0, 0,  7, 3, 0],
    [0, 0, 2,  0, 0, 9,  0, 6, 0],

    [2, 0, 0,  0, 0, 0,  4, 0, 9],
    [0, 0, 0,  0, 7, 0,  0, 0, 0],
    [6, 0, 9,  0, 0, 0,  0, 0, 1],

    [0, 8, 0,  4, 0, 0,  1, 0, 0],
    [0, 6, 3,  0, 0, 0,  0, 8, 0],
    [0, 0, 0,  6, 0, 8,  0, 0, 0]]

# Model definition
model = cp_model.CpModel()

# Decision Variables: 9x9 grid with values 1 to 9
grid = []
for i in range(9):
    row = []
    for j in range(9):
        if input_grid[i][j] != 0:
            # Fixed cell from input
            cell = model.NewIntVar(input_grid[i][j], input_grid[i][j], f'cell_{i}_{j}')
        else:
            # Empty cell to be filled
            cell = model.NewIntVar(1, 9, f'cell_{i}_{j}')
        row.append(cell)
    grid.append(row)

# Constraints

# Rows must have all different values
for i in range(9):
    model.AddAllDifferent(grid[i])

# Columns must have all different values
for j in range(9):
    col = [grid[i][j] for i in range(9)]
    model.AddAllDifferent(col)

# 3x3 subgrids must have all different values
for box_row in range(3):
    for box_col in range(3):
        block = []
        for i in range(3):
            for j in range(3):
                block.append(grid[box_row * 3 + i][box_col * 3 + j])
        model.AddAllDifferent(block)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solved_grid = []
    for i in range(9):
        solved_row = []
        for j in range(9):
            solved_row.append(solver.Value(grid[i][j]))
        solved_grid.append(solved_row)
    solution = {'grid': solved_grid}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")