
import cpmpy as cp
import numpy as np
import json

# Data (optional)
input_matrix = [
    [33, 30, 10, -6, 18, -7, -11, 23, -6],
    [16, -19, 9, -26, -8, -19, -8, -21, -14],
    [17, 12, -14, 31, -30, 13, -13, 19, 16],
    [-6, -11, 1, 17, -12, -4, -7, 14, -21],
    [18, -31, 34, -22, 17, -19, 20, 24, 6],
    [33, -18, 17, -15, 31, -5, 3, 27, -3],
    [-18, -20, -18, 31, 6, 4, -2, -12, 24],
    [27, 14, 4, -29, -3, 5, -29, 8, -12],
    [-15, -7, -23, 23, -9, -8, 6, 8, -12],
    [33, -23, -19, -4, -8, -7, 11, -12, 31],
    [-20, 19, -15, -30, 11, 32, 7, 14, -5],
    [-23, 18, -32, -2, -31, -7, 8, 24, 16],
    [32, -4, -10, -14, -6, -1, 0, 23, 23],
    [25, 0, -23, 22, 12, 28, -27, 15, 4],
    [-30, -13, -16, -3, -3, -32, -3, 27, -31],
    [22, 1, 26, 4, -2, -13, 26, 17, 14],
    [-9, -18, 3, -20, -27, -32, -11, 27, 13],
    [-17, 33, -7, 19, -32, 13, -31, -2, -24],
    [-31, 27, -31, -29, 15, 2, 29, -15, 33],
    [-18, -23, 15, 28, 0, 30, -4, 12, -32],
    [-3, 34, 27, -25, -18, 26, 1, 34, 26],
    [-21, -31, -10, -13, -30, -17, -12, -26, 31],
    [23, -31, -19, 21, -17, -10, 2, -23, 23],
    [-3, 6, 0, -3, -32, 0, -10, -25, 14],
    [-19, 9, 14, -27, 20, 15, -5, -27, 18],
    [11, -6, 24, 7, -17, 26, 20, -31, -25],
    [-25, 4, -16, 30, 33, 23, -4, -4, 23]
]
A = np.array(input_matrix, dtype=int)
nrows, ncols = A.shape

# Precompute constants
row_base = np.sum(A, axis=1).astype(int)
col_base = np.sum(A, axis=0).astype(int)
total_base = int(np.sum(A))

# Model definition
model = cp.Model()

# Decision Variables
# R[i]=1 means row i is flipped (-1), 0 means not flipped (+1)
# C[j]=1 means column j is flipped (-1), 0 means not flipped (+1)
R = cp.boolvar(shape=nrows, name="R")
C = cp.boolvar(shape=ncols, name="C")
# X[i,j] = R[i] XOR C[j], indicates if entry (i,j) is flipped (-1) relative to original
X = cp.boolvar(shape=(nrows, ncols), name="X")

# Constraints
# Link X with R and C: X[i,j] == R[i] XOR C[j]
model += [X[i, j] == (R[i] ^ C[j]) for i in range(nrows) for j in range(ncols)]

# Row sums nonnegative after flips:
# row_sum_i = row_base[i] - 2 * sum_j A[i,j] * X[i,j] >= 0
for i in range(nrows):
    model += (int(row_base[i]) - 2 * cp.sum(A[i, :] * X[i, :])) >= 0

# Column sums nonnegative after flips:
# col_sum_j = col_base[j] - 2 * sum_i A[i,j] * X[i,j] >= 0
for j in range(ncols):
    model += (int(col_base[j]) - 2 * cp.sum(A[:, j] * X[:, j])) >= 0

# Objective (optional)
# Minimize total sum after flips:
# total = total_base - 2 * sum_{i,j} A[i,j] * X[i,j]
objective = total_base - 2 * cp.sum(A * X)
model.minimize(objective)

# Solve and print
if model.solve():
    # Convert boolean R,C into -1/1 signs: sign = 1 - 2*val
    row_signs = [int(1 - 2 * int(R[i].value())) for i in range(nrows)]
    col_signs = [int(1 - 2 * int(C[j].value())) for j in range(ncols)]
    solution = {'row_signs': row_signs, 'col_signs': col_signs}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
