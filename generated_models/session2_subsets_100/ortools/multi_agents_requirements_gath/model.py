import json

from ortools.sat.python import cp_model

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
values = [81, 21, 79, 4, 29, 70, 28, 20, 14, 7]  # Given set A
n = len(values)

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables
in_S = [model.NewBoolVar(f"in_S[{i}]") for i in range(n)]
in_T = [model.NewBoolVar(f"in_T[{i}]") for i in range(n)]

# ---------------------------------------------------------------------------
# Constraints
# ---------------------------------------------------------------------------
# 1. Disjointness: an item cannot be in both subsets
for i in range(n):
    model.Add(in_S[i] + in_T[i] <= 1)

# 2. Non-emptiness of S and T
model.Add(sum(in_S) >= 1)
model.Add(sum(in_T) >= 1)

# 3. Equal subset sums
model.Add(sum(values[i] * in_S[i] for i in range(n)) ==
          sum(values[i] * in_T[i] for i in range(n)))

# ---------------------------------------------------------------------------
# Solve
# ---------------------------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 10  # safeguard, problem is tiny
status = solver.Solve(model)

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    in_S_result = [int(solver.Value(var)) for var in in_S]
    in_T_result = [int(solver.Value(var)) for var in in_T]
    print(json.dumps({"in_S": in_S_result, "in_T": in_T_result}))
else:
    # In the unlikely event no solution is found (should not happen here)
    print(json.dumps({"in_S": [], "in_T": []}))
