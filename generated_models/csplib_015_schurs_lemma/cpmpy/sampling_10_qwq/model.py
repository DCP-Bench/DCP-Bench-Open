
import cpmpy as cp
import json

# Input data
n = 13
c = 3

# Decision variables: balls[i] is the box (1, 2, or 3) for ball (i+1)
balls = cp.intvar(1, 3, shape=n)

model = cp.Model()

# Generate all triples (x, y, z) where x + y = z and z <= n
triples = []
for x in range(1, n+1):
    for y in range(x, n+1):  # Start from x to avoid duplicate pairs (x,y) and (y,x)
        z = x + y
        if z <= n:
            triples.append((x, y, z))

# Add constraints for each triple: not all three in the same box
for x, y, z in triples:
    bx = balls[x-1]  # balls are 0-indexed
    by = balls[y-1]
    bz = balls[z-1]
    model += ~((bx == by) & (by == bz))

# Solve
if model.solve():
    solution = {'balls': balls.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
