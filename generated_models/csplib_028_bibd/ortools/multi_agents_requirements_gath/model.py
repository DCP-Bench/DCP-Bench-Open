import json
from ortools.sat.python import cp_model

# -------------------------------------------------------------
# Input data (immutable)
# -------------------------------------------------------------
v = 9   # number of distinct objects (points)
b = 12  # number of blocks
r = 4   # each object occurs in exactly r blocks
k = 3   # each block contains exactly k objects
l = 1   # every pair of objects occurs together in exactly λ blocks

# -------------------------------------------------------------
# Model creation
# -------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables: matrix[i][j] = 1 if object i is in block j
matrix = []
for i in range(v):
    row = []
    for j in range(b):
        row.append(model.NewBoolVar(f"x_{i}_{j}"))
    matrix.append(row)

# -------------------------------------------------------------
# Constraints
# -------------------------------------------------------------
# 1. Row-sum constraint: every object appears in exactly r blocks
for i in range(v):
    model.Add(sum(matrix[i][j] for j in range(b)) == r)

# 2. Column-sum constraint: every block contains exactly k objects
for j in range(b):
    model.Add(sum(matrix[i][j] for i in range(v)) == k)

# 3. Pairwise balance constraint: every pair of objects appears together
#    in exactly λ blocks.  We linearise the product with auxiliary booleans.
for i1 in range(v):
    for i2 in range(i1 + 1, v):
        prod_vars = []
        for j in range(b):
            p = model.NewBoolVar(f"p_{i1}_{i2}_{j}")
            # p == matrix[i1][j] * matrix[i2][j]
            model.AddMultiplicationEquality(p, [matrix[i1][j], matrix[i2][j]])
            prod_vars.append(p)
        model.Add(sum(prod_vars) == l)

# -------------------------------------------------------------
# (Optional) small symmetry breaking – fixes first block to contain the
# first k objects.  This dramatically reduces the search space without
# affecting feasibility.
# -------------------------------------------------------------
for i in range(v):
    if i < k:
        model.Add(matrix[i][0] == 1)  # objects 0,1,2 are in block 0
    else:
        model.Add(matrix[i][0] == 0)

# -------------------------------------------------------------
# Solve
# -------------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 60  # safety cap
status = solver.Solve(model)

# -------------------------------------------------------------
# Output
# -------------------------------------------------------------
if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
    solution_matrix = [[int(solver.Value(matrix[i][j])) for j in range(b)] for i in range(v)]
    print(json.dumps({"matrix": solution_matrix}))
else:
    print(json.dumps({"matrix": None}))
