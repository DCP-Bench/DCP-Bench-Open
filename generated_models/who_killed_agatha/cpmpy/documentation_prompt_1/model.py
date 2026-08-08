
import cpmpy as cp
import json

names = ["Agatha herself", "the butler", "Charles"]
n = len(names)

model = cp.Model()

# Variables
# killer: index of the killer (0=Agatha, 1=butler, 2=Charles)
killer = cp.intvar(0, n-1, name="killer")

# hates[i,j] = 1 if person i hates person j, else 0
hates = cp.boolvar(shape=(n, n), name="hates")

# richer[i,j] = 1 if person i is richer than person j, else 0
richer = cp.boolvar(shape=(n, n), name="richer")

# Constraints

# 1) A killer always hates their victim (Agatha, index 0)
model += hates[killer, 0] == 1

# 2) A killer is no richer than their victim (Agatha)
# So killer richer than Agatha is false
model += richer[killer, 0] == 0

# 3) Charles hates no one that Agatha hates
# For all j: if Agatha hates j then Charles does not hate j
for j in range(n):
    model += hates[2, j].implies(~hates[0, j])

# 4) Agatha hates everybody except the butler
# Agatha hates 0 (herself) and 2 (Charles), but not 1 (butler)
for j in range(n):
    if j == 1:
        model += hates[0, j] == 0
    else:
        model += hates[0, j] == 1

# 5) The butler hates everyone not richer than Aunt Agatha
# i.e. for all j: if j is not richer than Agatha, butler hates j
# "not richer than Agatha" means richer[j,0] == 0
for j in range(n):
    model += hates[1, j] == (richer[j, 0] == 0)

# 6) The butler hates everyone whom Agatha hates
# For all j: if Agatha hates j then butler hates j
for j in range(n):
    model += hates[0, j].implies(hates[1, j])

# 7) No one hates everyone
# For all i: hates[i] is not all ones
for i in range(n):
    model += cp.sum(hates[i, :]) <= n - 1

# 8) Richer relation is irreflexive: no one is richer than themselves
for i in range(n):
    model += richer[i, i] == 0

# 9) Richer relation is antisymmetric: if i richer than j then j not richer than i
for i in range(n):
    for j in range(n):
        if i != j:
            model += richer[i, j].implies(~richer[j, i])

# 10) The problem does not explicitly say if richer is total or partial order.
# We do not enforce totality, only antisymmetry and irreflexivity.

# Solve and print
if model.solve():
    solution = {'killer': int(killer.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
