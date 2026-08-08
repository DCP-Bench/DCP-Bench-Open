import json
from ortools.sat.python import cp_model

# --------------------------------------------------
# 1. Input data (exactly as provided)
# --------------------------------------------------
n = 5  # size of the grid (given)

# --------------------------------------------------
# 2. Derived constants
# --------------------------------------------------
N = n * n  # highest number to be placed

# --------------------------------------------------
# 3. Model
# --------------------------------------------------
model = cp_model.CpModel()

# Coordinates for every value k = 1..N
rows = [model.NewIntVar(0, n - 1, f"row_{k}") for k in range(N)]
cols = [model.NewIntVar(0, n - 1, f"col_{k}") for k in range(N)]

# Encoded position to apply AllDifferent in one shot
positions = [model.NewIntVar(0, N - 1, f"pos_{k}") for k in range(N)]
for k in range(N):
    # pos = row * n + col (n is constant)
    model.Add(positions[k] == rows[k] * n + cols[k])

# Each square contains at most one number and each number occupies exactly one square
model.AddAllDifferent(positions)

# --------------------------------------------------
# 4. Allowed successor moves (pre-computed table)
# --------------------------------------------------
allowed_pairs = []  # tuples (r_k, c_k, r_{k+1}, c_{k+1})
move_vectors = [  # (dr, dc)
    (0, 3), (0, -3),  # horizontal type I
    (3, 0), (-3, 0),  # vertical   type I
    (2, 2), (2, -2), (-2, 2), (-2, -2),  # diagonal type II
]
for r in range(n):
    for c in range(n):
        for dr, dc in move_vectors:
            r2, c2 = r + dr, c + dc
            if 0 <= r2 < n and 0 <= c2 < n:
                allowed_pairs.append([r, c, r2, c2])

# Successor constraints for every consecutive pair (k, k+1)
for k in range(N - 1):
    model.AddAllowedAssignments([rows[k], cols[k], rows[k + 1], cols[k + 1]], allowed_pairs)

# --------------------------------------------------
# 5. (Optional) symmetry breaking — fix the first number in a corner
# --------------------------------------------------
model.Add(rows[0] == 0)
model.Add(cols[0] == 0)

# --------------------------------------------------
# 6. Solver configuration and search
# --------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30  # safety limit

status = solver.Solve(model)

# --------------------------------------------------
# 7. Extract and print solution as required JSON
# --------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    # Build the n x n grid
    grid = [[0 for _ in range(n)] for _ in range(n)]
    for k in range(N):
        r = solver.Value(rows[k])
        c = solver.Value(cols[k])
        grid[r][c] = k + 1  # because k is 0-based index for value k+1
    print(json.dumps({"x": grid}))
else:
    # If no solution is found, still print JSON with empty list to respect the contract
    print(json.dumps({"x": []}))
