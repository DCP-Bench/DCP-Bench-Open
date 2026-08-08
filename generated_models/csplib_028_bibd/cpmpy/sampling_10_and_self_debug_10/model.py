
import cpmpy as cp
import json

# Data
v = 9   # Number of distinct objects (rows)
b = 12  # Number of blocks (columns)
r = 4   # Number of blocks each object occurs in (row sum)
k = 3   # Number of objects each block contains (column sum)
l = 1   # Number of blocks in which each pair of distinct objects occurs together (scalar product between rows)

# Model definition
model = cp.Model()

# Decision Variables
# incidence matrix: v x b binary matrix
matrix = cp.boolvar(shape=(v, b), name="matrix")

# Constraints
# Each row sum is exactly r
for i in range(v):
    model += (cp.sum(matrix[i, :]) == r)

# Each column sum is exactly k
for j in range(b):
    model += (cp.sum(matrix[:, j]) == k)

# Scalar product (dot product) of any two distinct rows is exactly l
for i in range(v):
    for j in range(i + 1, v):
        # sum over columns of matrix[i][c]*matrix[j][c] == l
        # Because matrix entries are 0/1, product is AND (logical and)
        # We can model scalar product as sum of element-wise AND:
        # Since cpmpy does not support direct multiplication of boolvars, we use cp.logical_and
        # But cpmpy does not support elementwise logical_and on variables, so we need to use:
        # scalar product = sum over c of matrix[i,c] * matrix[j,c]
        # Since variables are 0/1, multiplication is equivalent to and.
        # cpmpy supports multiplication of boolvars.
        scalar_prod = cp.sum([matrix[i, c] * matrix[j, c] for c in range(b)])
        model += (scalar_prod == l)

# Solve and print
if model.solve():
    solution = {'matrix': matrix.value().astype(int).tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
