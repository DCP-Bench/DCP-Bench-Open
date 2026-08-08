
import cpmpy as cp
import json

# Data
n = 13  # Number of balls
c = 3   # Number of boxes
# End of data

# Model definition
model = cp.Model()

# Decision Variables: M[i,j] == 1 iff ball i+1 is in box j+1
M = cp.intvar(0, 1, shape=(n, c), name="M")

# Constraints
# Each ball is in exactly one box
for i in range(n):
    model += (cp.sum([M[i, j] for j in range(c)]) == 1)

# For each triple x + y = z, not all three are in the same box.
# We iterate x <= y to avoid duplicate triples (x,y) and (y,x).
for x in range(1, n + 1):
    for y in range(x, n + 1):
        z = x + y
        if z <= n:
            xi = x - 1
            yi = y - 1
            zi = z - 1
            for j in range(c):
                model += (cp.sum([M[xi, j], M[yi, j], M[zi, j]]) <= 2)

# Solve
if model.solve():
    M_val = M.value().tolist()
    # convert row of 0/1 to box index 1..c
    balls = [row.index(1) + 1 for row in M_val]
    solution = {'balls': balls}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
