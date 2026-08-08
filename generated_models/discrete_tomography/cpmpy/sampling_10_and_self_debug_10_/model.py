
import cpmpy as cp
import json

# Data
row_sums = [0, 0, 8, 2, 6, 4, 5, 3, 7, 0, 0]
col_sums = [0, 0, 7, 1, 6, 3, 4, 5, 2, 7, 0, 0]
R = len(row_sums)
C = len(col_sums)
# End of data

# Model definition
model = cp.Model()

# Decision Variables: binary matrix R x C
matrix = cp.intvar(0, 1, shape=(R, C), name="matrix")

# Constraints: row sums and column sums
for i in range(R):
    model += cp.sum(matrix[i, :]) == row_sums[i]
for j in range(C):
    model += cp.sum(matrix[:, j]) == col_sums[j]

# Solve and print
if model.solve():
    solution = {'matrix': matrix.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
