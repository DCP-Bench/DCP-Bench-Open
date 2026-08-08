# OR-Tools CP-SAT model for the fixed-length N-Puzzle feasibility task
# --------------------------------------------------------------
# This file is completely self-contained:
# * parses the input that is hard-coded below
# * builds the CP model so that every constraint in the requirement
#   document is enforced
# * searches for any sequence of exactly N legal moves that takes the
#   start configuration to the goal configuration
# * prints the solution as JSON with the single key "steps" as required

from ortools.sat.python import cp_model
import json

# ---------------------------------------------------------------------
# 1. Immutable input data (exactly as supplied in the exercise)
# ---------------------------------------------------------------------
N = 20  # Number of steps to the solution
puzzle_start = [  # Start state of the puzzle, 0 represents the empty tile
    [0, 3, 6],
    [2, 4, 8],
    [1, 7, 5]
]

puzzle_end = [  # End state of the puzzle
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

# ---------------------------------------------------------------------
# 2. Derived constants
# ---------------------------------------------------------------------
R = len(puzzle_start)          # number of rows
C = len(puzzle_start[0])       # number of columns
num_tiles = R * C              # |V|
all_values = range(num_tiles)  # 0..R*C-1

# ---------------------------------------------------------------------
# 3. Helper ranges for nicer loops
# ---------------------------------------------------------------------
T_full = range(N + 1)   # 0 .. N (inclusive)  – states INCLUDING the start
T_move = range(1, N + 1)  # 1 .. N  – states after a move (used for diffs)
rows = range(R)
cols = range(C)

# ---------------------------------------------------------------------
# 4. CP-SAT model
# ---------------------------------------------------------------------
model = cp_model.CpModel()

# 4.1. Decision variables – board positions for every time step
x = {}
for t in T_full:
    for r in rows:
        for c in cols:
            var_name = f"x_{t}_{r}_{c}"
            if t == 0:
                # fixed to the start configuration
                v = puzzle_start[r][c]
                x[t, r, c] = model.NewConstant(v)
            elif t == N:
                # fixed to the goal configuration
                v = puzzle_end[r][c]
                x[t, r, c] = model.NewConstant(v)
            else:
                x[t, r, c] = model.NewIntVar(0, num_tiles - 1, var_name)

# 4.2. All-Different (Permutation) constraint for every state
for t in T_full:
    flat = [x[t, r, c] for r in rows for c in cols]
    model.AddAllDifferent(flat)

# 4.3. Boolean indicators for the empty tile (value 0)
#      and integer coordinates (rowZero, colZero) per state
rowZero = {}
colZero = {}
for t in T_full:
    # Boolean matrix: isZero[t][r][c] == 1  <=>  x[t,r,c] == 0
    isZero = {}
    for r in rows:
        for c in cols:
            b = model.NewBoolVar(f"isZero_{t}_{r}_{c}")
            isZero[r, c] = b
            model.Add(x[t, r, c] == 0).OnlyEnforceIf(b)
            model.Add(x[t, r, c] != 0).OnlyEnforceIf(b.Not())
    # Exactly one zero per board
    model.Add(sum(isZero.values()) == 1)

    # Row and column of the zero tile
    rowZero[t] = model.NewIntVar(0, R - 1, f"rowZero_{t}")
    colZero[t] = model.NewIntVar(0, C - 1, f"colZero_{t}")

    model.Add(rowZero[t] == sum(r * isZero[r, c] for r in rows for c in cols))
    model.Add(colZero[t] == sum(c * isZero[r, c] for r in rows for c in cols))

# 4.4. Move legality between consecutive states (t-1) -> t
for t in T_move:
    # 4.4.1. Manhattan adjacency of the empty tile
    diff_row = model.NewIntVar(-R, R, f"diff_row_{t}")
    diff_col = model.NewIntVar(-C, C, f"diff_col_{t}")
    model.Add(diff_row == rowZero[t] - rowZero[t - 1])
    model.Add(diff_col == colZero[t] - colZero[t - 1])

    abs_row = model.NewIntVar(0, R, f"abs_row_{t}")
    abs_col = model.NewIntVar(0, C, f"abs_col_{t}")
    model.AddAbsEquality(abs_row, diff_row)
    model.AddAbsEquality(abs_col, diff_col)
    model.Add(abs_row + abs_col == 1)  # Manhattan distance == 1

    # 4.4.2. Exactly two positions differ (the swap of 0 with the tile)
    diff_bools = []
    for r in rows:
        for c in cols:
            d = model.NewBoolVar(f"diff_{t}_{r}_{c}")
            diff_bools.append(d)
            model.Add(x[t, r, c] != x[t - 1, r, c]).OnlyEnforceIf(d)
            model.Add(x[t, r, c] == x[t - 1, r, c]).OnlyEnforceIf(d.Not())
    model.Add(sum(diff_bools) == 2)

# ---------------------------------------------------------------------
# 5. Invoke the solver (pure feasibility, no objective)
# ---------------------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0  # safety guard – can be adjusted
status = solver.Solve(model)

# ---------------------------------------------------------------------
# 6. Output handling – produce the required JSON when a solution is found
# ---------------------------------------------------------------------
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    steps = []  # will contain N states (1 .. N)
    for t in T_move:  # 1 .. N
        board = []
        for r in rows:
            row_list = []
            for c in cols:
                row_list.append(int(solver.Value(x[t, r, c])))
            board.append(row_list)
        steps.append(board)

    print(json.dumps({"steps": steps}))
else:
    # According to the assumptions the instance should be solvable;
    # if not, still print a valid JSON so that the checker can fail cleanly.
    print(json.dumps({"steps": []}))
