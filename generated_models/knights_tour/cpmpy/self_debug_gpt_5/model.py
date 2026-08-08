
import cpmpy as cp
import json

# Data
n = 6  # size of the chessboard (changeable)
N = n * n

# Precompute knight move edges between cell ids
# Cell id mapping: id = r*n + c
edges = []
deltas = [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]
for r in range(n):
    for c in range(n):
        u = r * n + c
        for dr, dc in deltas:
            r2, c2 = r + dr, c + dc
            if 0 <= r2 < n and 0 <= c2 < n:
                v = r2 * n + c2
                edges.append([u, v])
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# x[r][c] is the move number (0..N-1) assigned to cell (r,c)
x = cp.intvar(0, N-1, shape=(n, n), name="x")
# pos[k] is the cell id (0..N-1) where move number k is placed
pos = cp.intvar(0, N-1, shape=N, name="pos")

# Constraints
# Link x and pos via inverse permutation channeling
# a[id] = x at cell id, pos[k] = id of cell with move k
a = x.reshape(N)
model += cp.Inverse(a, pos)

# Start at top-left corner to break symmetries
model += (x[0, 0] == 0)  # hence pos[0] == 0

# Consecutive moves must be knight moves
for k in range(N - 1):
    model += cp.Table([pos[k], pos[k + 1]], edges)

# Objective (none, satisfaction problem)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
