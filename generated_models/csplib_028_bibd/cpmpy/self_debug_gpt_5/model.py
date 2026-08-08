
import cpmpy as cp
import json

# Data
v = 9   # Number of distinct objects
b = 12  # Number of blocks
r = 4   # Number of blocks each object occurs in
k = 3   # Number of objects each block contains
l = 1   # Number of blocks in which each pair of distinct objects occurs together
# End of data

# Model definition
model = cp.Model()

# Decision Variables: incidence matrix (v x b) with boolean entries
matrix = cp.boolvar(shape=(v, b), name="matrix")

# Constraints
# 1) Each row has exactly r ones
for i in range(v):
    model += (cp.sum(matrix[i, :]) == r)

# 2) Each column has exactly k ones
for j in range(b):
    model += (cp.sum(matrix[:, j]) == k)

# 3) Pairwise scalar product between distinct rows equals l
for i in range(v):
    for j in range(i + 1, v):
        model += (cp.sum([matrix[i, c] & matrix[j, c] for c in range(b)]) == l)

# Symmetry breaking: fix the first row to have its r ones in the first r columns
for c in range(b):
    model += (matrix[0, c] == (1 if c < r else 0))

# Solve and print
if model.solve():
    # Convert boolean matrix to list of lists of integers (0/1)
    mat_list = [[int(val) for val in row] for row in matrix.value().tolist()]
    solution = {'matrix': mat_list}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
