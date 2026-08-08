
import cpmpy as cp
import json

# Data
n = 13  # Number of balls
c = 3   # Number of boxes
# End of data

# Model definition
model = cp.Model()

# Decision Variables: M[i,j] == 1 if ball i+1 is in box j+1
M = cp.boolvar(shape=(n, c))

# Constraints
# Each ball must be in exactly one box
for i in range(n):
    model += cp.sum(M[i, :]) == 1

# For any x, y, z with x + y = z, no monochromatic triple in any box
for x in range(1, n + 1):
    for y in range(x, n + 1):  # x <= y to avoid duplicate pairs
        z = x + y
        if z <= n:
            for j in range(c):
                # M[x-1,j] + M[y-1,j] + M[z-1,j] <= 2
                model += M[x-1, j] + M[y-1, j] + M[z-1, j] <= 2

# Solve and print
if model.solve():
    # Extract assignment: for each ball, find the box number (1..c)
    # M.value() is an (n x c) array of 0/1
    assign = (M.value().argmax(axis=1) + 1).tolist()
    solution = {'balls': assign}
    print(json.dumps(solution))
else:
    print("No solution found.")
