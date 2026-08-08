
from ortools.sat.python import cp_model
import json

# Input data
names = ["Agatha herself", "the butler", "Charles"]

# Model definition
model = cp_model.CpModel()

# Decision Variables
# hates[i][j] = True if person i hates person j
hates = [[model.NewBoolVar(f"hates_{i}_{j}") for j in range(3)] for i in range(3)]
# richer[i][j] = True if person i is richer than person j
richer = [[model.NewBoolVar(f"richer_{i}_{j}") for j in range(3)] for i in range(3)]

# Killer index (0=Agatha,1=butler,2=Charles), but killer != Agatha so domain is [1,2]
killer = model.NewIntVar(1, 2, "killer")

# Auxiliary booleans for conditional constraints
is_killer1 = model.NewBoolVar("is_killer1")  # butler
is_killer2 = model.NewBoolVar("is_killer2")  # Charles

# Link killer to the auxiliary booleans
model.Add(is_killer1 + is_killer2 == 1)
model.Add(killer == 1).OnlyEnforceIf(is_killer1)
model.Add(killer == 2).OnlyEnforceIf(is_killer2)

# No one hates themselves and no one is richer than themselves
for i in range(3):
    model.Add(hates[i][i] == 0)
    model.Add(richer[i][i] == 0)

# Prevent contradictory richer relationships: i richer than j and j richer than i cannot both hold
for i in range(3):
    for j in range(i + 1, 3):
        model.Add(richer[i][j] + richer[j][i] <= 1)

# 1) A killer always hates, and is no richer than, his victim (Agatha = 0)
model.Add(hates[1][0] == 1).OnlyEnforceIf(is_killer1)
model.Add(richer[1][0] == 0).OnlyEnforceIf(is_killer1)
model.Add(hates[2][0] == 1).OnlyEnforceIf(is_killer2)
model.Add(richer[2][0] == 0).OnlyEnforceIf(is_killer2)

# 2) Charles hates no one that Agatha hates
for j in range(3):
    # skip self-case j=2? Actually we only enforce for j != 2 to avoid self-implication
    if j != 2:
        # if Agatha hates j then Charles does not hate j
        model.AddBoolOr([hates[0][j].Not(), hates[2][j].Not()])

# 3) Agatha hates everybody except the butler (1)
model.Add(hates[0][1] == 0)
for j in range(3):
    if j not in (0, 1):
        model.Add(hates[0][j] == 1)

# 4) The butler hates everyone not richer than Aunt Agatha (0)
for j in range(3):
    if j != 1:
        # if j is not richer than Agatha, the butler hates j
        model.AddImplication(richer[j][0].Not(), hates[1][j])

# 5) The butler hates everyone whom Agatha hates
for j in range(3):
    if j != 1:
        model.AddImplication(hates[0][j], hates[1][j])

# 6) No one hates everyone (each person must have at least one 'no-hate')
for i in range(3):
    # sum of hates to others <= number_of_others - 1  => at least one False
    model.Add(sum(hates[i][j] for j in range(3) if j != i) <= 1)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'killer': solver.Value(killer)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
