
import cpmpy as cp
import json

# Board size (n x n). You can change n to other sizes (e.g., 6). n=5 is chosen for a reasonably fast solve.
n = 5
N = n * n

# Precompute valid knight moves as pairs of cell indices (from_index, to_index)
moves = []
for i in range(N):
    r1 = i // n
    c1 = i % n
    for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
        r2 = r1 + dr
        c2 = c1 + dc
        if 0 <= r2 < n and 0 <= c2 < n:
            j = r2 * n + c2
            moves.append((i, j))

# Model
model = cp.Model()

# Decision variables:
# inv[t] = cell index (0..N-1) visited at time t
inv = cp.intvar(0, N-1, shape=N, name="inv")

# x is the chessboard: x[r][c] = move number (0..N-1) when that square is visited
x = cp.intvar(0, N-1, shape=(n, n), name="x")

# Also create a flattened version of x to use with the Inverse constraint
x_flat = cp.intvar(0, N-1, shape=N, name="x_flat")

# Link x_flat and x matrix
for idx in range(N):
    r = idx // n
    c = idx % n
    model += (x_flat[idx] == x[r, c])

# Inverse constraint between inv and x_flat:
# x_flat[cell] = time step when cell is visited, inv[time] = cell visited at that time
model += cp.Inverse(inv, x_flat)

# All times must be different (each time maps to a different cell)
model += cp.AllDifferent(inv)

# Knight move constraints: consecutive times must correspond to valid knight moves
for t in range(N - 1):
    # (inv[t], inv[t+1]) must be one of the allowed knight move pairs
    model += cp.Table([inv[t], inv[t + 1]], moves)

# Ensure the tour is open (does NOT return to the starting square):
# forbid the pair (inv[N-1], inv[0]) from being a knight move
model += cp.NegativeTable([inv[N - 1], inv[0]], moves)

# Symmetry breaking: fix the starting square to reduce search (optional)
model += (inv[0] == 0)

# Solve
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
