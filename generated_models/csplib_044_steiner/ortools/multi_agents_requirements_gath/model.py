import json
from ortools.sat.python import cp_model

# ------------------------------------------------------------------
# Input data (immutable – do NOT touch)
# ------------------------------------------------------------------
n = 9  # Order of the Steiner Triple System

# ------------------------------------------------------------------
# Derived constants
# ------------------------------------------------------------------
B = n * (n - 1) // 6     # number of triples (blocks)   => 12 for n=9
r = (n - 1) // 2         # replication number per element => 4 for n=9

# ------------------------------------------------------------------
# CP-SAT model
# ------------------------------------------------------------------
model = cp_model.CpModel()

# Decision variables: x[b][i] == 1  iff element i (0-based) is in block b (0-based)
x = [[model.NewBoolVar(f"x_{b}_{i}") for i in range(n)]
     for b in range(B)]

# Helper variables for each (block, pair)
y = {}  # key = (b,i,j) with i<j
pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
for b in range(B):
    for (i, j) in pairs:
        y[(b, i, j)] = model.NewBoolVar(f"y_{b}_{i}_{j}")
        # y == AND(x[b][i], x[b][j])
        model.Add(y[(b, i, j)] <= x[b][i])
        model.Add(y[(b, i, j)] <= x[b][j])
        model.Add(y[(b, i, j)] >= x[b][i] + x[b][j] - 1)

# ------------------------------------------------------------------
# Constraints
# ------------------------------------------------------------------
# 1. Each block contains exactly three elements
for b in range(B):
    model.Add(sum(x[b][i] for i in range(n)) == 3)

# 2. Each unordered pair appears in exactly one block
for (i, j) in pairs:
    model.Add(sum(y[(b, i, j)] for b in range(B)) == 1)

# 3. Each element appears exactly r times  (redundant but strengthens search)
for i in range(n):
    model.Add(sum(x[b][i] for b in range(B)) == r)

# 4. Simple symmetry-breaking: fix first block to {1,2,3}
model.Add(x[0][0] == 1)
model.Add(x[0][1] == 1)
model.Add(x[0][2] == 1)
for i in range(3, n):
    model.Add(x[0][i] == 0)

# ------------------------------------------------------------------
# Solve
# ------------------------------------------------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30.0
solver.parameters.num_search_workers = 8  # utilise multi-core when available

status = solver.Solve(model)
if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError("No Steiner Triple System found for n=9 within the time limit.")

# ------------------------------------------------------------------
# Extract solution
# ------------------------------------------------------------------
solution_sets = []
for b in range(B):
    triple = [i + 1 for i in range(n) if solver.BooleanValue(x[b][i])]
    triple.sort()
    solution_sets.append(triple)

# Sort blocks lexicographically for deterministic output
solution_sets.sort()

# ------------------------------------------------------------------
# Output – strictly JSON with the required key
# ------------------------------------------------------------------
print(json.dumps({"sets": solution_sets}))