
import cpmpy as cp
import json

# Board size
n = 5
N = n * n

# Model definition
model = cp.Model()

# Decision Variables
# x is the chessboard: x[r,c] is the move number (0..N-1) when the knight visits (r,c)
x = cp.intvar(0, N - 1, shape=(n, n), name="x")

# Flattened version of x for convenience: x_flat[i] corresponds to cell index i (row major)
x_flat = cp.intvar(0, N - 1, shape=N, name="x_flat")
for i in range(N):
    r = i // n
    c = i % n
    model += (x_flat[i] == x[r, c])

# All cells must have distinct move numbers 0..N-1
model += cp.AllDifferent(x_flat)

# pos_idx[v] = index (0..N-1) of the cell that has move number v
pos_idx = cp.intvar(0, N - 1, shape=N, name="pos_idx")
model += cp.Inverse(x_flat, pos_idx)

# row[v], col[v] are the coordinates of the square visited at move v
row = cp.intvar(0, n - 1, shape=N, name="row")
col = cp.intvar(0, n - 1, shape=N, name="col")
for v in range(N):
    model += (pos_idx[v] == row[v] * n + col[v])

# Knight move constraints: for each consecutive moves v and v+1, positions must be a knight move apart
for v in range(N - 1):
    dr = cp.Abs(row[v] - row[v + 1])
    dc = cp.Abs(col[v] - col[v + 1])
    # (1,2) or (2,1)
    model += ((dr == 1) & (dc == 2)) | ((dr == 2) & (dc == 1))

# Symmetry breaking: fix the starting square (optional, speeds up search)
model += (x[0, 0] == 0)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
