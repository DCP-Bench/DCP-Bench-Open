# Hay-bale puzzle solved with Google OR-Tools CP-SAT
# ---------------------------------------------------
# Five bales are weighed in every two-bale combination. Given the ten pair
# weights, recover each individual bale weight.
#
# Expected JSON output keys: ['bales']

from ortools.sat.python import cp_model
import json

# --------------------------------------------------
# 1. Input data (immutable)
# --------------------------------------------------
# All ten unordered pair weights, already sorted
W = [80, 82, 83, 84, 85, 86, 87, 88, 90, 91]
N_BALES = 5                       # number of bales

# --------------------------------------------------
# 2. Model
# --------------------------------------------------
model = cp_model.CpModel()

# Decision variables:   bales[i] = weight of bale i (kg)
# Bounds: positive integers; loose upper bound 100 kg covers all possibilities
bales = [model.NewIntVar(1, 100, f"bale_{i}") for i in range(N_BALES)]

# Optional symmetry-breaking: non-decreasing order
for i in range(N_BALES - 1):
    model.Add(bales[i] <= bales[i + 1])

# Pre-compute all 10 unordered pairs  (i < j)
pair_vars = []                    # sum variables = bales[i] + bales[j]
allowed_domain = cp_model.Domain.FromValues(W)  # every sum must be one of W

for i in range(N_BALES):
    for j in range(i + 1, N_BALES):
        s = model.NewIntVarFromDomain(allowed_domain, f"s_{i}_{j}")
        model.Add(s == bales[i] + bales[j])       # definition of the sum
        pair_vars.append(s)

# The recorded weights are *all different*, therefore each sum variable must
# take a distinct value from W – together they form a permutation of W.
model.AddAllDifferent(pair_vars)

# --------------------------------------------------
# 3. Solve (feasibility problem)
# --------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

# --------------------------------------------------
# 4. Output
# --------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    solution = [int(solver.Value(b)) for b in bales]
    print(json.dumps({"bales": solution}))
else:
    # According to the puzzle there *is* a solution, but guard just in case
    print(json.dumps({"bales": []}))
