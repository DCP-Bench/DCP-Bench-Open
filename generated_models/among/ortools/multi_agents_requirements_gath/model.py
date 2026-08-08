# -------------------------------------------------------------
#  Google OR-Tools CP-SAT model for the "exactly m in v" problem
# -------------------------------------------------------------
# Requirement recap:
#   • n = 5 variables x[0..4]
#   • Exactly m = 3 of them must take a value from the set v = {1, 5, 8}
#   • Pure feasibility problem – any assignment satisfying the rule is fine
#   • Output must be JSON with the single key "x"
# -------------------------------------------------------------

from ortools.sat.python import cp_model
import json

# -------------------------
# 1. Input data (immutable)
# -------------------------
n = 5            # Length of vector x
m = 3            # Exactly this many x[i] must be in v
v = [1, 5, 8]    # The value set that must appear exactly m times

# -------------------------
# 2. Model creation
# -------------------------
model = cp_model.CpModel()

# Decision variables: x[0..n-1]
# We need a domain that contains both the allowed values in v and some values outside v
# so that the remaining (n-m) positions can take something not in v.  A small, fixed
# range 0..10 is sufficient and keeps the model simple.
X_DOMAIN_MIN = 0
X_DOMAIN_MAX = 10

x = [model.NewIntVar(X_DOMAIN_MIN, X_DOMAIN_MAX, f"x[{i}]") for i in range(n)]

# Optional auxiliary indicator variables: y[i] == 1   ⇔   x[i] ∈ v
y = [model.NewBoolVar(f"y[{i}]") for i in range(n)]

# Link each (x[i], y[i]) pair via a table (allowed assignments)
# If the value is in v, y[i] must be 1; otherwise y[i] must be 0.
allowed_tuples = []
for val in range(X_DOMAIN_MIN, X_DOMAIN_MAX + 1):
    in_set = 1 if val in v else 0
    allowed_tuples.append([val, in_set])

for i in range(n):
    model.AddAllowedAssignments([x[i], y[i]], allowed_tuples)

# Cardinality constraint: exactly m indices with x[i] in v → sum(y) == m
model.Add(sum(y) == m)

# -------------------------
# 3. Solve the model
# -------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# -------------------------
# 4. Extract & print result
# -------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution_x = [solver.Value(var) for var in x]
    print(json.dumps({"x": solution_x}))
else:
    # No feasible solution (should not occur with the given data)
    print(json.dumps({"x": []}))
