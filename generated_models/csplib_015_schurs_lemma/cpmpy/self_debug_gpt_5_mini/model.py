
import cpmpy as cp
import json

# Data
n = 13  # Number of balls
c = 3   # Number of boxes
# End of data

# Model definition
model = cp.Model()

# Decision Variables: M[i,j] = 1 iff ball i (1-based) is in box j (1-based)
M = cp.intvar(0, 1, shape=(n, c), name="M")

# Constraints

# Each ball is in exactly one box
for i in range(n):
    model += (cp.sum(M[i, :]) == 1)

# For every x,y with z = x + y <= n, prevent x,y,z all being in the same box j
for x in range(1, n + 1):
    for y in range(1, n + 1):
        z = x + y
        if z <= n:
            for j in range(c):
                model += (M[x - 1, j] + M[y - 1, j] + M[z - 1, j] <= 2)

# Solve and print
if model.solve():
    M_val = M.value().tolist()
    # Convert each ball's row to the box index 1..c
    balls = [next(idx for idx, val in enumerate(row) if val == 1) + 1 for row in M_val]
    solution = {'balls': balls}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
