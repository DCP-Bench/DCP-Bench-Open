
import cpmpy as cp
import json

# Guests indexed as:
# 0: Andrew
# 1: Betty
# 2: Cara
# 3: Dave
# 4: Erica
# 5: Frank

# Allowed neighbors for each guest (by index)
allowed_neighbors = {
    0: {3, 5},      # Andrew: Dave, Frank
    1: {2, 4},      # Betty: Cara, Erica
    2: {1, 5},      # Cara: Betty, Frank
    3: {0, 4},      # Dave: Andrew, Erica
    4: {1, 3},      # Erica: Betty, Dave
    5: {0, 2}       # Frank: Andrew, Cara
}

n = 6  # number of guests/seats

model = cp.Model()

# Decision variable: x[i] = guest seated at seat i (0..5)
x = cp.intvar(0, n-1, shape=n, name="x")

# All guests must be seated exactly once
model += cp.AllDifferent(x)

# Conflict variables for each adjacent pair (0 or 1)
conflicts = cp.intvar(0, 1, shape=n, name="conflicts")

# Precompute allowed pairs as a set of tuples including both directions
allowed_pairs = set()
for g in range(n):
    for nb in allowed_neighbors[g]:
        allowed_pairs.add((g, nb))
        allowed_pairs.add((nb, g))  # add symmetric pair

# For each adjacent pair, create boolean variables indicating if the pair matches any allowed pair
for i in range(n):
    g1 = x[i]
    g2 = x[(i+1) % n]

    # For each allowed pair, create a boolean variable indicating if (g1,g2) == allowed_pair
    match_bools = []
    for (a, b) in allowed_pairs:
        bvar = cp.boolvar()
        # bvar is true iff g1 == a and g2 == b
        model += (bvar == ((g1 == a) & (g2 == b)))
        match_bools.append(bvar)

    # conflicts[i] = 1 if none of the allowed pairs match, else 0
    model += conflicts[i] == 1 - cp.sum(match_bools)

# Objective: minimize total conflicts
model.minimize(cp.sum(conflicts))

if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
