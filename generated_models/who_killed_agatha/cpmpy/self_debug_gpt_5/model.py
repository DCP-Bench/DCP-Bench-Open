
import cpmpy as cp
import json

# Data (optional)
names = ["Agatha herself", "the butler", "Charles"]
n = len(names)
AGATHA, BUTLER, CHARLES = 0, 1, 2
# End of data

# Model definition
model = cp.Model()

# Decision Variables
hates = cp.boolvar(shape=(n, n), name="hates")     # hates[i,j]: person i hates person j
richer = cp.boolvar(shape=(n, n), name="richer")   # richer[i,j]: person i is strictly richer than person j
killer = cp.intvar(0, n-1, name="killer")          # index of the killer

# Constraints

# Basic properties of 'richer': irreflexive and not both directions
for i in range(n):
    model += (richer[i, i] == 0)
for i in range(n):
    for j in range(n):
        if i != j:
            model += ~(richer[i, j] & richer[j, i])

# No one hates everyone
for i in range(n):
    model += (cp.sum(hates[i, :]) <= n - 1)

# Charles hates no one that Agatha hates: if Agatha hates j then Charles does not hate j
for j in range(n):
    model += hates[AGATHA, j].implies(~hates[CHARLES, j])

# Agatha hates everybody except the butler
for j in range(n):
    model += (hates[AGATHA, j] == (1 if j != BUTLER else 0))

# The butler hates everyone not richer than Aunt Agatha:
# for all j, if not (j richer than Agatha) then Butler hates j
for j in range(n):
    model += (~richer[j, AGATHA]).implies(hates[BUTLER, j])

# The butler hates everyone whom Agatha hates
for j in range(n):
    model += hates[AGATHA, j].implies(hates[BUTLER, j])

# Killer constraints: killer hates the victim (Agatha) and is no richer than the victim
for i in range(n):
    model += (killer == i).implies(hates[i, AGATHA])
    model += (killer == i).implies(~richer[i, AGATHA])

# Solve and print
if model.solve():
    solution = {'killer': int(killer.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
