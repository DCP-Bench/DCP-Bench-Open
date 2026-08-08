
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

# For each triple (x,y,z) with x + y = z, and for each box j,
# not all three balls are in the same box
for z in range(1, n+1):
    for x in range(1, z):
        y = z - x
        if y >= 1 and y <= n:
            for j in range(c):
                # M[x-1,j] + M[y-1,j] + M[z-1,j] <= 2
                model += (M[x-1, j] + M[y-1, j] + M[z-1, j] <= 2)

# Solve and print
if model.solve():
    # balls[i] = box number (1-based) for ball i+1
    balls = [int(cp.sum([M[i, j] * (j+1) for j in range(c)]).value()) for i in range(n)]
    solution = {'balls': balls}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
