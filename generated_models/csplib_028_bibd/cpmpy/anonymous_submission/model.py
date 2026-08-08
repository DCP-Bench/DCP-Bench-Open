# Import libraries
from cpmpy import *
import json

# Parameters
v = 9  # Number of distinct objects
b = 12  # Number of blocks
r = 4  # Number of blocks each object occurs in
k = 3  # Number of objects each block contains
l = 1  # Number of blocks in which each pair of distinct objects occurs together

# Decision Variables
matrix = boolvar(shape=(v, b), name="matrix")  # Incidence matrix of the BIBD

# Model
model = Model()

# Constraint: each block contains exactly k distinct objects
for j in range(b):
    model += sum(matrix[:, j]) == k

# Constraint: each object occurs in exactly r different blocks
for i in range(v):
    model += sum(matrix[i, :]) == r

# Constraint: every two distinct objects occur together in exactly l blocks
for i1 in range(v):
    for i2 in range(i1 + 1, v):
        model += sum([matrix[i1,j] * matrix[i2,j] for j in range(b)]) == l

# Solve
model.solve()

# Print solution
solution = {"matrix": matrix.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script