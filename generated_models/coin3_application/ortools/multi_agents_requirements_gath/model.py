import json
from ortools.sat.python import cp_model

# -------------------------------------------------------------
# Problem data (fixed, no external input)
# -------------------------------------------------------------
DENOM = [1, 2, 5, 10, 20, 50]  # coin values in cents (ascending)
MAX_PAYABLE = 99               # we must be able to pay any value 1..99
NUM_DENOMS = len(DENOM)

# -------------------------------------------------------------
# CP-SAT model
# -------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables: x[d] = number of coins of denomination DENOM[d]
# Upper bound: with value v we can never need more than 99 // v coins.
x = [model.NewIntVar(0, MAX_PAYABLE // val, f"x_{val}") for val in DENOM]

# Auxiliary variables: y[v][d] = coins of denom d used to pay amount v
# Needed to enforce that every value 1..99 can be paid with existing stock.
y = {}
for v in range(1, MAX_PAYABLE + 1):
    row = []
    for d, val in enumerate(DENOM):
        y_vd = model.NewIntVar(0, v // val, f"y_{v}_{val}")  # cannot exceed v/val
        row.append(y_vd)
        # cannot use more coins than available
        model.Add(y_vd <= x[d])
    # exact payment constraint for amount v
    model.Add(sum(y_vd * val for y_vd, val in zip(row, DENOM)) == v)
    y[v] = row  # (kept only to preserve handles; not used after build)

# Objective: minimise total number of coins kept
model.Minimize(sum(x))

# -------------------------------------------------------------
# Solve model
# -------------------------------------------------------------
solver = cp_model.CpSolver()
# allow parallel search for speed
solver.parameters.num_search_workers = 8
status = solver.Solve(model)

# -------------------------------------------------------------
# Output in required JSON format
# -------------------------------------------------------------
if status == cp_model.OPTIMAL:
    result = [solver.Value(var) for var in x]
    print(json.dumps({"x": result}))
else:
    # No feasible solution found (should not happen); return empty list
    print(json.dumps({"x": []}))