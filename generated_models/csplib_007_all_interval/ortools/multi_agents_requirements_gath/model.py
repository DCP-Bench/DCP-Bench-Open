"""All-Interval Series (n = 12)

A feasible all-interval series is an ordering x[0..11] of the twelve pitch-classes
{0,…,11} such that the absolute intervals between consecutive notes form the set
{1,…,11} exactly once.  This script builds the classical constraint programming
model with Google OR-Tools CP-SAT, solves it, and prints one solution as JSON
with the mandatory keys ['diffs', 'x'].
"""

from ortools.sat.python import cp_model
import json

# -------------------------------------------------------------
# Immutable input data (as supplied in the task description)
# -------------------------------------------------------------
n = 12  # number of pitch-classes / length of the series

# -------------------------------------------------------------
# Model
# -------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables
x = [model.NewIntVar(0, n - 1, f"x[{i}]") for i in range(n)]          # pitch-classes
intervals = [model.NewIntVar(1, n - 1, f"diffs[{i}]") for i in range(n - 1)]  # absolute intervals

# 1. The pitch-classes form a permutation of Z_n
model.AddAllDifferent(x)

# 2. The intervals form a permutation of {1,…,n-1}
model.AddAllDifferent(intervals)

# 3. Definition of intervals   intervals[i] = |x[i+1] – x[i]|
for i in range(n - 1):
    model.AddAbsEquality(intervals[i], x[i + 1] - x[i])

# Optional but standard symmetry breaking:
# Fix first pitch-class to 0 (eliminates rotational symmetries)
model.Add(x[0] == 0)
# No additional symmetry constraint is imposed so that the instance remains
# satisfiable for n = 12 (the largest interval 11 requires x[1] = 11).

# Helpful redundant constraint: sum of 1..11 = 66
model.Add(sum(intervals) == n * (n - 1) // 2)

# -------------------------------------------------------------
# Solver configuration
# -------------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0  # safety cap – usually solved instantly
solver.parameters.num_search_workers = 8      # use several CPU cores if available

status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError("No feasible all-interval series found (status = %s)" % solver.StatusName(status))

# -------------------------------------------------------------
# Extract and print solution
# -------------------------------------------------------------
solution_x = [solver.Value(v) for v in x]
solution_intervals = [solver.Value(v) for v in intervals]

print(json.dumps({
    "diffs": solution_intervals,
    "x": solution_x
}))
