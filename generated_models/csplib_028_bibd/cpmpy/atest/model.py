# Import libraries
from cpmpy import *
import json

# Parameters
v = 9  # Number of distinct objects
b = 12  # Number of blocks
r = 4  # Number of blocks each object occurs in
k = 3  # Number of objects each block contains
l = 1  # Number of blocks in which each pair of distinct objects occurs together

# Decision variables
matrix = boolvar(shape=(v, b), name="matrix")

# Model
model = Model()

# Each row (object) has exactly r ones
for i in range(v):
    model += [sum(matrix[i, :]) == r]

# Each column (block) has exactly k ones
for j in range(b):
    model += [sum(matrix[:, j]) == k]

# Any pair of distinct rows has exactly l ones in common (dot product)
for i in range(v):
    for j in range(i + 1, v):
        model += [sum([matrix[i, col] * matrix[j, col] for col in range(b)]) == l]

# Solve the model
model.solve()

# Print the solution
solution = {"matrix": matrix.value().tolist()}
print(json.dumps(solution))