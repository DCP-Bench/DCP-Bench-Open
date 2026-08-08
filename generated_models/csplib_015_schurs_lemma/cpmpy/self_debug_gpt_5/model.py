
import cpmpy as cp
import json

# Data (optional)
n = 13  # Number of balls
c = 3   # Number of boxes
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# balls[i] is the box (1..c) assigned to ball i+1
balls = cp.intvar(1, c, shape=n, name="balls")

# Constraints
# For every triple (x, y, z) with x + y = z, they cannot all be in the same box
for x in range(1, n+1):
    for y in range(1, n+1):
        z = x + y
        if z <= n:
            model += ~cp.AllEqual(balls[x-1], balls[y-1], balls[z-1])

# Objective (optional)
# Satisfaction problem: no objective

# Solve and print
if model.solve():
    solution = {'balls': balls.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
