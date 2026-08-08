
import cpmpy as cp
import json

# Data
v = 9  # Number of distinct objects (rows)
b = 12  # Number of blocks (columns)
r = 4  # Number of blocks each object occurs in (row sum)
k = 3  # Number of objects each block contains (column sum)
l = 1  # Number of blocks in which each pair of distinct objects occurs together (pairwise dot product)
# End of data

# Model definition
model = cp.Model()

# Decision Variables: incidence matrix v x b of 0/1
matrix = cp.intvar(0, 1, shape=(v, b), name="matrix")

# Constraints
# Each row has exactly r ones
for i in range(v):
    model += cp.sum(matrix[i, :]) == r

# Each column has exactly k ones
for j in range(b):
    model += cp.sum(matrix[:, j]) == k

# Any two distinct rows have scalar product l
for i in range(v):
    for j in range(i + 1, v):
        model += cp.sum(matrix[i, :] * matrix[j, :]) == l

# Symmetry breaking: lexicographic non-decreasing order of rows to help the solver
model += cp.LexChainLessEq(matrix)

# Solve
if model.solve():
    solution = {'matrix': matrix.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
