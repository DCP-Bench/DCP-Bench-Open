import json
from ortools.sat.python import cp_model

# -------------------------
# Input data (immutable)
# -------------------------
n = 10  # Size of the chessboard and number of queens

# -------------------------
# Model creation
# -------------------------
model = cp_model.CpModel()

# Decision variables
# queens[r] represents the column (0..n-1) where the queen is placed in row r.
queens = [model.NewIntVar(0, n - 1, f"q_{r}") for r in range(n)]

# -------------------------
# Constraints
# -------------------------
# 1. All columns must be different
model.AddAllDifferent(queens)

# 2. Diagonal constraints
#    Major diagonal (row - col)  -> use (queen - row) must be different
#    Minor diagonal (row + col)  -> use (queen + row) must be different
model.AddAllDifferent([queens[r] + r for r in range(n)])
model.AddAllDifferent([queens[r] - r for r in range(n)])

# -------------------------
# No objective (pure feasibility)
# -------------------------

# Solver
solver = cp_model.CpSolver()
# Optional: limit time or set a log if desired (kept minimal here)
status = solver.Solve(model)

# -------------------------
# Output
# -------------------------
if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
    solution_queens = [solver.Value(var) for var in queens]
    print(json.dumps({"queens": solution_queens}))
else:
    # According to the problem statement, a solution exists for n = 10;
    # If not found (e.g. due to unexpected issues), we still output a valid JSON.
    print(json.dumps({"queens": []}))
