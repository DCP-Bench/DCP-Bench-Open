
import cpmpy as cp
import json

# Data
n = 13  # Number of balls
c = 3   # Number of boxes
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# M[i,j] = 1 if ball i+1 is in box j+1, else 0
M = cp.boolvar(shape=(n, c), name="M")

# Constraints
# Each ball must be in exactly one box
for i in range(n):
    model += (cp.sum(M[i, :]) == 1)

# For each triple (x,y,z) with x + y = z, no triple (x,y,z) are all in the same box
# We consider x,y,z in 1..n, and x+y=z
for x in range(1, n+1):
    for y in range(x, n+1):  # start y from x to avoid duplicates
        z = x + y
        if z <= n:
            for j in range(c):
                # M[x-1,j] + M[y-1,j] + M[z-1,j] <= 2
                model += (M[x-1, j] + M[y-1, j] + M[z-1, j] <= 2)

# Solve and print
if model.solve():
    # For each ball, find the box assigned (index + 1)
    balls = [int(cp.sum([M[i, j] * (j+1) for j in range(c)]).value()) for i in range(n)]
    solution = {'balls': balls}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
