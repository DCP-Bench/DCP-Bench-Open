import json
from ortools.sat.python import cp_model

# --------------------------------------------------
# Input data (do not modify)
# --------------------------------------------------
names = ["Agatha herself", "the butler", "Charles"]
P = range(3)      # 0 = Agatha, 1 = butler, 2 = Charles
VICTIM = 0        # index of Aunt Agatha

# --------------------------------------------------
# Model
# --------------------------------------------------
model = cp_model.CpModel()

# Decision variable: who is the killer?  Boolean indicator for each person.
killer = [model.NewBoolVar(f"killer_{i}") for i in P]  # exactly one is True

# Auxiliary variables -------------------------------------------------------
# hates[i][j] == 1  iff person i hates person j
hates = [[model.NewBoolVar(f"hates_{i}_{j}") for j in P] for i in P]

# richer[i][j] == 1 iff person i is strictly richer than person j
richer = [[model.NewBoolVar(f"richer_{i}_{j}") for j in P] for i in P]

# --------------------------------------------------
# Constraints
# --------------------------------------------------
# C1: Exactly one killer
model.Add(sum(killer) == 1)

# C2: The killer hates the victim (Agatha)
for i in P:
    model.Add(hates[i][VICTIM] >= killer[i])

# C3: The killer is not richer than the victim
for i in P:
    # If i is the killer (killer[i] == 1) then richer[i][victim] must be 0.
    # Linear encoding:  richer[i][0] + killer[i] <= 1
    model.Add(richer[i][VICTIM] + killer[i] <= 1)

# C4: Charles hates no one that Agatha hates
#     For every person j: hates[Agatha][j] = 1 -> hates[Charles][j] = 0
for j in P:
    model.Add(hates[0][j] + hates[2][j] <= 1)

# C5: Explicit hatred pattern for Agatha
#     Agatha hates everybody except the butler.
model.Add(hates[0][0] == 1)  # hates herself
model.Add(hates[0][1] == 0)  # does NOT hate the butler
model.Add(hates[0][2] == 1)  # hates Charles

# C6: The butler hates everyone not richer than Agatha
for j in P:
    # if richer[j][Agatha] == 0 then hates[butler][j] == 1
    # Linear: hates[1][j] >= 1 - richer[j][0]
    model.Add(hates[1][j] >= 1 - richer[j][0])

# C7: The butler hates everyone whom Agatha hates
for j in P:
    model.Add(hates[1][j] >= hates[0][j])

# C8: No one hates everyone (i.e., can hate at most 2 people)
for i in P:
    model.Add(sum(hates[i][j] for j in P) <= 2)

# C9: Richness relation properties
for i in P:
    # Irreflexive: nobody richer than themselves
    model.Add(richer[i][i] == 0)
    for j in P:
        if i != j:
            # Antisymmetric: at most one of richer[i][j] and richer[j][i] is true
            model.Add(richer[i][j] + richer[j][i] <= 1)

# C10: Transitivity of "richer than"
for i in P:
    for j in P:
        for k in P:
            model.Add(richer[i][j] + richer[j][k] - 1 <= richer[i][k])

# --------------------------------------------------
# Solve
# --------------------------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError("No feasible solution found for the murder mystery.")

# Extract killer index
killer_index = next(i for i in P if solver.Value(killer[i]) == 1)

# --------------------------------------------------
# Output (must be JSON with the required key)
# --------------------------------------------------
print(json.dumps({"killer": killer_index}))
