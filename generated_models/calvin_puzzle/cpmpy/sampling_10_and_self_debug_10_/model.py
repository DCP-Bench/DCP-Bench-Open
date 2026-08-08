
import cpmpy as cp
import json

# Data
n = 5
N = n * n
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# Position row and column for each number k (1..N). Use 0-based indexing for rows/cols.
pos_r = cp.intvar(0, n-1, shape=N, name="pos_r")
pos_c = cp.intvar(0, n-1, shape=N, name="pos_c")

# Flattened position index for each number: idx = r*n + c (0..N-1)
pos_idx = cp.intvar(0, N-1, shape=N, name="pos_idx")

# The grid x: x[i,j] is the number placed at row i, col j (values 1..N)
x = cp.intvar(1, N, shape=(n, n), name="x")

# Build a flat list of x variables for element constraints and AllDifferent
x_flat = [x[i, j] for i in range(n) for j in range(n)]

# Constraints

# Link pos_idx to pos_r and pos_c
for k in range(N):
    model += (pos_idx[k] == pos_r[k] * n + pos_c[k])

# Each position index must be unique (each cell used exactly once by some number)
model += cp.AllDifferent(pos_idx)

# The grid values are a permutation of 1..N
model += cp.AllDifferent(x_flat)

# Link positions to grid values: the cell at position pos_idx[k] must contain number k+1
# Use cp.Element to index x_flat by the (variable) position index
for k in range(N):
    model += cp.Element(x_flat, pos_idx[k]) == (k + 1)

# Movement constraints between successive numbers
# For k -> k+1 the move must be either:
#  - orthogonal by exactly 3 squares (|dr| == 3 and dc == 0) or (|dc| == 3 and dr == 0)
#  - diagonal by exactly 2 squares (|dr| == 2 and |dc| == 2)
for k in range(N - 1):
    dr = pos_r[k+1] - pos_r[k]
    dc = pos_c[k+1] - pos_c[k]
    orth1 = (cp.Abs(dr) == 3) & (dc == 0)
    orth2 = (cp.Abs(dc) == 3) & (dr == 0)
    diag = (cp.Abs(dr) == 2) & (cp.Abs(dc) == 2)
    model += (orth1 | orth2 | diag)

# No objective, just find a feasible filling
# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
