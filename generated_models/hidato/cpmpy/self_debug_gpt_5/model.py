
import cpmpy as cp
import numpy as np
import json

# Data (optional)
puzzle = [[0, 0, 134, 2, 4, 0, 0, 0, 0, 0, 0, 0],
          [136, 0, 0, 1, 0, 5, 6, 10, 115, 106, 0, 0],
          [139, 0, 0, 124, 0, 122, 117, 0, 0, 107, 0, 0],
          [0, 131, 126, 0, 123, 0, 0, 12, 0, 0, 0, 103],
          [0, 0, 144, 0, 0, 0, 0, 0, 14, 0, 99, 101],
          [0, 0, 129, 0, 23, 21, 0, 16, 65, 97, 96, 0],
          [30, 29, 25, 0, 0, 19, 0, 0, 0, 66, 94, 0],
          [32, 0, 0, 27, 57, 59, 60, 0, 0, 0, 0, 92],
          [0, 40, 42, 0, 56, 58, 0, 0, 72, 0, 0, 0],
          [0, 39, 0, 0, 0, 0, 78, 73, 71, 85, 69, 0],
          [35, 0, 0, 46, 53, 0, 0, 0, 80, 84, 0, 0],
          [36, 0, 45, 0, 0, 52, 51, 0, 0, 0, 0, 88]]
# End of data

# Dimensions
R = len(puzzle)
C = len(puzzle[0])
N = R * C  # numbers 1..N

# Model definition
model = cp.Model()

# Decision Variables
# x[r,c] holds the number (1..N) in cell (r,c)
x = cp.intvar(1, N, shape=(R, C), name="x")

# Auxiliary variables for permutation and positions
# y[r,c] = x[r,c] - 1 in 0..N-1 for using cp.Inverse
y = cp.intvar(0, N-1, shape=(R, C), name="y")
# z[k] is the cell index (0..N-1) where number k (0-based) is placed
z = cp.intvar(0, N-1, shape=N, name="z")

# Constraints
# Channel x and y
model += (x == y + 1)

# Bijective mapping between cells and numbers
y_flat = y.flatten()
model += cp.Inverse(y_flat, z)

# Adjacency constraints: consecutive numbers must be neighbors (8-directional)
for k in range(N - 1):
    r_k = z[k] // C
    c_k = z[k] % C
    r_n = z[k + 1] // C
    c_n = z[k + 1] % C
    model += (cp.Abs(r_k - r_n) <= 1)
    model += (cp.Abs(c_k - c_n) <= 1)

# Fix givens
for r in range(R):
    for c in range(C):
        v = puzzle[r][c]
        if v != 0:
            model += (x[r, c] == v)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
