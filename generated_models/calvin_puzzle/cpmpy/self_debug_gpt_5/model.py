
import cpmpy as cp
import json

# Data (optional)
n = 5
N = n * n
# End of data

# Helper to compute linear index and moves
def idx_to_rc(idx):
    return idx // n, idx % n

def rc_to_idx(r, c):
    return r * n + c

# Precompute allowed move pairs (u,v) based on the rules
moves = [(3,0), (-3,0), (0,3), (0,-3), (2,2), (2,-2), (-2,2), (-2,-2)]
edges = []
for u in range(N):
    r, c = idx_to_rc(u)
    for dr, dc in moves:
        r2, c2 = r + dr, c + dc
        if 0 <= r2 < n and 0 <= c2 < n:
            v = rc_to_idx(r2, c2)
            edges.append([u, v])

# Model definition
model = cp.Model()

# Decision Variables
# pos[i] is the linearized cell index (0..N-1) where number i+1 is placed
pos = cp.intvar(0, N-1, shape=N, name="pos")
# num0[j] is the number index (0..N-1) placed at cell j
num0 = cp.intvar(0, N-1, shape=N, name="num0")
# x is the grid with values 1..N
x = cp.intvar(1, N, shape=(n, n), name="x")

# Constraints
# Bijection between pos and num0
model += cp.Inverse(pos, num0)

# Consecutive numbers must follow allowed moves
for i in range(N - 1):
    model += cp.Table([pos[i], pos[i + 1]], edges)

# Channel x to num0 (+1 to convert 0-based num to 1..N)
x_flat = x.reshape(N)
for j in range(N):
    model += (x_flat[j] == num0[j] + 1)

# Objective (optional)
# No objective, just find any feasible solution

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
