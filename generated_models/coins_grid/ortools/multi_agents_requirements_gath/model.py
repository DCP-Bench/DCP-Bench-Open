# Coin placement on a 31x31 grid – CP-SAT model with Google OR-Tools
# ---------------------------------------------------------------
# The program builds and solves the optimisation model described in the task
# and prints the optimal placement and the corresponding distance sum as JSON.
# ---------------------------------------------------------------

from ortools.sat.python import cp_model
import json
import sys

# ---------------------------------------------------------------
# 1. Input parsing (none supplied, kept for completeness)
# ---------------------------------------------------------------
# The problem statement provides no external numerical input; all parameters
# are hard-coded according to the specifications.

# ---------------------------------------------------------------
# 2. Model parameters
# ---------------------------------------------------------------
N = 31            # board dimension (rows & columns)
R = 14            # coins per row
C = 14            # coins per column (same as R)
NB_COINS = R * N  # total number of coins (must equal C * N)
MAX_DIST = (N - 1) ** 2       # maximum squared distance for any single cell
Z_UB = NB_COINS * MAX_DIST    # very safe upper bound for the objective

# ---------------------------------------------------------------
# 3. Build CP-SAT model
# ---------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables: x[i][j] – 1 if a coin is placed in cell (i,j)
# (0-based indices used internally; distance formula uses (j-i)**2 which
# is identical to the 1-based version for squared differences.)
x = {}
for i in range(N):
    for j in range(N):
        x[i, j] = model.NewBoolVar(f"x_{i}_{j}")

# Row constraints – exactly R coins in each row
for i in range(N):
    model.Add(sum(x[i, j] for j in range(N)) == R)

# Column constraints – exactly C coins in each column
for j in range(N):
    model.Add(sum(x[i, j] for i in range(N)) == C)

# Objective variable z: total squared horizontal distance
expr = []
for i in range(N):
    for j in range(N):
        coeff = (j - i) ** 2
        if coeff:  # skip zero coefficients for a tiny speed-up
            expr.append(coeff * x[i, j])
# Add z variable explicitly because the requirements ask for it
z = model.NewIntVar(0, Z_UB, "z")
model.Add(z == sum(expr))
model.Minimize(z)

# ---------------------------------------------------------------
# 4. Solve the model
# ---------------------------------------------------------------
solver = cp_model.CpSolver()
# Optional: limit wall time to keep execution predictable (adjust as desired)
solver.parameters.max_time_in_seconds = 60.0
solver.parameters.num_search_workers = 8  # parallel search when available

status = solver.Solve(model)

# ---------------------------------------------------------------
# 5. Extract and print solution
# ---------------------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    # Build 0/1 matrix in row-major order
    matrix = []
    for i in range(N):
        row = [int(solver.BooleanValue(x[i, j])) for j in range(N)]
        matrix.append(row)
    result = {
        "x": matrix,
        "z": int(solver.Value(z)),
    }
else:
    # No solution was found within the time limit or model is infeasible.
    # To comply with the strict output spec, print an empty solution with z = -1.
    result = {
        "x": [[0] * N for _ in range(N)],
        "z": -1,
    }

# Sole required output
print(json.dumps(result))
