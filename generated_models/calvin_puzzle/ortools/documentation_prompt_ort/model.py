from ortools.sat.python import cp_model
import json

# Input data
n = 5

# Model definition
model = cp_model.CpModel()

# Decision Variables
# pos[i][j]: the number placed at cell (i,j), from 1 to n*n
pos = [[model.NewIntVar(1, n * n, f'pos_{i}_{j}') for j in range(n)] for i in range(n)]

# To facilitate constraints, create inverse mapping: for each number k, its position (row, col)
# row_pos[k-1], col_pos[k-1] are the coordinates of number k
row_pos = [model.NewIntVar(0, n - 1, f'row_pos_{k}') for k in range(n * n)]
col_pos = [model.NewIntVar(0, n - 1, f'col_pos_{k}') for k in range(n * n)]

# Constraints

# 1) All numbers from 1 to n*n appear exactly once in the grid
model.AddAllDifferent([pos[i][j] for i in range(n) for j in range(n)])

# 2) Link pos and (row_pos, col_pos)
# For each cell (i,j), pos[i][j] = k+1 <=> row_pos[k] = i and col_pos[k] = j
# We use element constraints to enforce this

# Create arrays for element constraints
# For each number k, row_pos[k] and col_pos[k] must correspond to the cell where pos[i][j] == k+1
# We enforce that for each k, pos[row_pos[k]][col_pos[k]] == k+1

for k in range(n * n):
    # row_pos[k] and col_pos[k] are indices, so we can use AddElement constraints
    # But AddElement requires 1D arrays, so we flatten pos
    # pos_flat[index] = pos[i][j], index = i*n + j
    pos_flat = [pos[i][j] for i in range(n) for j in range(n)]
    # index = row_pos[k]*n + col_pos[k]
    index = model.NewIntVar(0, n * n - 1, f'index_{k}')
    model.Add(index == row_pos[k] * n + col_pos[k])
    model.AddElement(index, pos_flat, k + 1)

# 3) For each consecutive pair k and k+1 (k from 1 to n*n-1), the position of k+1 must be reachable from k by the movement rules

for k in range(n * n - 1):
    r1 = row_pos[k]
    c1 = col_pos[k]
    r2 = row_pos[k + 1]
    c2 = col_pos[k + 1]

    dr = model.NewIntVar(-n + 1, n - 1, f'dr_{k}')
    dc = model.NewIntVar(-n + 1, n - 1, f'dc_{k}')
    model.Add(dr == r2 - r1)
    model.Add(dc == c2 - c1)

    abs_dr = model.NewIntVar(0, n - 1, f'abs_dr_{k}')
    abs_dc = model.NewIntVar(0, n - 1, f'abs_dc_{k}')
    model.AddAbsEquality(abs_dr, dr)
    model.AddAbsEquality(abs_dc, dc)

    # Movement Type I: vertical or horizontal move exactly 3 squares away (gap of 2 squares)
    # So either abs_dr == 3 and abs_dc == 0
    # or abs_dr == 0 and abs_dc == 3

    # Movement Type II: diagonal move exactly 2 squares away (gap of 1 square)
    # So abs_dr == 2 and abs_dc == 2

    # Create boolean variables for each movement type
    move_type_I_vert = model.NewBoolVar(f'move_type_I_vert_{k}')
    move_type_I_horiz = model.NewBoolVar(f'move_type_I_horiz_{k}')
    move_type_II_diag = model.NewBoolVar(f'move_type_II_diag_{k}')

    model.Add(abs_dr == 3).OnlyEnforceIf(move_type_I_vert)
    model.Add(abs_dc == 0).OnlyEnforceIf(move_type_I_vert)
    model.Add(abs_dr != 3).OnlyEnforceIf(move_type_I_vert.Not())
    model.Add(abs_dc != 0).OnlyEnforceIf(move_type_I_vert.Not())

    model.Add(abs_dr == 0).OnlyEnforceIf(move_type_I_horiz)
    model.Add(abs_dc == 3).OnlyEnforceIf(move_type_I_horiz)
    model.Add(abs_dr != 0).OnlyEnforceIf(move_type_I_horiz.Not())
    model.Add(abs_dc != 3).OnlyEnforceIf(move_type_I_horiz.Not())

    model.Add(abs_dr == 2).OnlyEnforceIf(move_type_II_diag)
    model.Add(abs_dc == 2).OnlyEnforceIf(move_type_II_diag)
    model.Add(abs_dr != 2).OnlyEnforceIf(move_type_II_diag.Not())
    model.Add(abs_dc != 2).OnlyEnforceIf(move_type_II_diag.Not())

    # Exactly one of these movement types must be true
    model.AddBoolOr([move_type_I_vert, move_type_I_horiz, move_type_II_diag])
    model.AddBoolAnd([move_type_I_vert.Not(), move_type_I_horiz.Not(), move_type_II_diag.Not()]).OnlyEnforceIf(
        model.NewBoolVar(f'false_{k}').Not())  # just to avoid contradiction, no effect

    model.AddExactlyOne([move_type_I_vert, move_type_I_horiz, move_type_II_diag])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    x = [[solver.Value(pos[i][j]) for j in range(n)] for i in range(n)]
    solution = {'x': x}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")