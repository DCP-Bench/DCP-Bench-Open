# Import libraries
from cpmpy import *
import json

# Parameters
n = 13  # Number of balls
c = 3  # Number of boxes

# Decision variables
# M[i][j] is True if ball i is in box j
M = boolvar(shape=(n, c), name="M")

# Model
model = Model()

# Each ball must be in exactly one box
for i in range(n):
    model += [sum(M[i, :]) == 1]

# For each triple (x, y, z) such that x + y = z, ensure that not all are in the same box
# Generate all valid (x, y, z) such that x + y = z and x < y < z
for x in range(n):
    for y in range(x + 1, n):
        z = x + y
        if z < n:
            for j in range(c):
                model += [M[x, j] + M[y, j] + M[z, j] <= 2]

# Solve the model
model.solve()

# Convert the solution to a list of box assignments for each ball
balls = [0] * n
for i in range(n):
    for j in range(c):
        if M[i, j].value():
            balls[i] = j + 1  # boxes are labeled from 1 to 3

# Print the solution
solution = {"balls": balls}
print(json.dumps(solution))