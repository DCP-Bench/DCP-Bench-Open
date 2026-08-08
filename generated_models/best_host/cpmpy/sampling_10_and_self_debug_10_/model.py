
import cpmpy as cp
import json

# Data: allowed neighbors for each guest
# 0: Andrew, 1: Betty, 2: Cara, 3: Dave, 4: Erica, 5: Frank
allowed_neighbors = {
    0: [3, 5],  # Andrew -> Dave, Frank
    1: [2, 4],  # Betty -> Cara, Erica
    2: [1, 5],  # Cara -> Betty, Frank
    3: [0, 4],  # Dave -> Andrew, Erica
    4: [1, 3],  # Erica -> Betty, Dave
    5: [0, 2],  # Frank -> Andrew, Cara
}

# Build allowed matrix and flattened version for element indexing
n = 6
allowed = [[0]*n for _ in range(n)]
for i in range(n):
    for j in allowed_neighbors[i]:
        allowed[i][j] = 1
allowed_flat = [allowed[i][j] for i in range(n) for j in range(n)]  # length 36

# Model definition
model = cp.Model()

# Decision Variables
# x is seating order around the table (positions 0..5). Values are guests 0..5.
x = cp.intvar(0, n-1, shape=n, name="x")
model += cp.AllDifferent(x)

# Conflict variables for each adjacent pair (circular)
conf = cp.intvar(0, 1, shape=n, name="conf")

# Constraints: conf[k] == 1 if the pair x[k], x[(k+1)%n] is NOT allowed (i.e., allowed==0)
for k in range(n):
    nxt = (k+1) % n
    idx = x[k]*n + x[nxt]  # index into allowed_flat (0..35)
    # conf == 1 - allowed[x[k], x[nxt]]
    model += conf[k] == 1 - cp.Element(allowed_flat, idx)

# Objective: minimize total conflicts
model.minimize(cp.sum(conf))

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
