from ortools.sat.python import cp_model
import json

# Input data
names = ["Agatha herself", "the butler", "Charles"]
n = len(names)

# Model definition
model = cp_model.CpModel()

# Variables
# hates[i][j] = 1 if person i hates person j, else 0
hates = []
for i in range(n):
    row = []
    for j in range(n):
        row.append(model.NewBoolVar(f'hates_{i}_{j}'))
    hates.append(row)

# richer[i][j] = 1 if person i is richer than person j, else 0
richer = []
for i in range(n):
    row = []
    for j in range(n):
        row.append(model.NewBoolVar(f'richer_{i}_{j}'))
    richer.append(row)

# killer is an integer variable in [0, n-1]
killer = model.NewIntVar(0, n - 1, 'killer')

# Constraints

# 1) A killer always hates, and is no richer than his victim.
# For all i,j: if killer == i and victim == j (Agatha is victim, index 0)
# then hates[i][j] == 1 and richer[i][j] == 0
for i in range(n):
    # killer == i => hates[i][0] == 1
    model.Add(hates[i][0] == 1).OnlyEnforceIf(killer == i)
    # killer == i => richer[i][0] == 0
    model.Add(richer[i][0] == 0).OnlyEnforceIf(killer == i)

# 2) Charles hates no one that Agatha hates.
# For all j: hates[Charles][j] <= hates[Agatha][j]
# Charles index = 2, Agatha index = 0
for j in range(n):
    model.AddImplication(hates[2][j].Not(), hates[0][j].Not())

# 3) Agatha hates everybody except the butler.
# Agatha index = 0, butler index = 1
for j in range(n):
    if j == 1:
        model.Add(hates[0][j] == 0)
    else:
        model.Add(hates[0][j] == 1)

# 4) The butler hates everyone not richer than Aunt Agatha.
# For all j: if richer[j][0] == 0 then hates[butler][j] == 1
# butler index = 1, Agatha index = 0
for j in range(n):
    # If person j is not richer than Agatha (richer[j][0] == 0), then butler hates j
    model.AddImplication(richer[j][0].Not(), hates[1][j])

# 5) The butler hates everyone whom Agatha hates.
# For all j: if hates[Agatha][j] == 1 then hates[butler][j] == 1
for j in range(n):
    model.AddImplication(hates[0][j], hates[1][j])

# 6) No one hates everyone.
# For all i: sum of hates[i][j] for j in [0..n-1] < n
for i in range(n):
    model.Add(sum(hates[i][j] for j in range(n)) <= n - 1)

# 7) Richer relation is irreflexive: no one is richer than themselves
for i in range(n):
    model.Add(richer[i][i] == 0)

# 8) Richer relation is antisymmetric: if i richer than j then j not richer than i
for i in range(n):
    for j in range(n):
        if i != j:
            model.AddBoolOr([richer[i][j].Not(), richer[j][i].Not()])

# 9) Richer relation is total order or partial order? Problem does not specify.
# We only need to satisfy constraints above.

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'killer': solver.Value(killer)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")