
import cpmpy as cp
import json

# Data
board = [[1, 0, 0, 2, 3],
         [0, 0, 0, 4, 0],
         [0, 0, 4, 0, 0],
         [0, 2, 3, 0, 5],
         [0, 1, 5, 0, 0]]
# End of data

n = len(board)
m = len(board[0])
colors = sorted(list({board[i][j] for i in range(n) for j in range(m)} - {0}))
if not colors:
    colors = list(range(1, 6))  # fallback, but here we have colors 1..5

# Find terminal positions for each color
terminals = {k: [] for k in colors}
for i in range(n):
    for j in range(m):
        if board[i][j] != 0:
            terminals[board[i][j]].append((i, j))

# Model definition
model = cp.Model()

# Decision Variables
B = cp.intvar(1, len(colors), shape=(n, m), name="B")  # color for each cell

# Path position variables for each color: Pk[u] = position along the path from the chosen source (0 if not color k)
max_len = n * m
P = {k: cp.intvar(0, max_len, shape=(n, m), name=f"P{k}") for k in colors}

# Constraints

# Fix given cells and assure all cells are colored 1..|colors|
for i in range(n):
    for j in range(m):
        if board[i][j] != 0:
            model += (B[i, j] == board[i][j])

# Helper: neighbors within grid
def neighbors(i, j):
    for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
        ni, nj = i+di, j+dj
        if 0 <= ni < n and 0 <= nj < m:
            yield ni, nj

# For each color, connect terminals with a single non-branching path that covers all cells of that color
for k in colors:
    # Identify the two terminals (source, sink)
    if len(terminals[k]) != 2:
        # If input malformed, no solution
        model += (1 == 0)
        continue
    (si, sj), (ti, tj) = terminals[k][0], terminals[k][1]

    # Channeling between B and Pk:
    # - If cell is color k then Pk>=1, else Pk==0
    for i in range(n):
        for j in range(m):
            is_k = (B[i, j] == k)
            model += is_k.implies(P[k][i, j] >= 1)
            model += (~is_k).implies(P[k][i, j] == 0)

    # Source has path position 1
    model += (P[k][si, sj] == 1)

    # Degree/orientation constraints using position differences:
    # For source: exactly one neighbor with +1, none with -1
    plus_source = cp.sum([ (B[ni, nj] == k) & (P[k][ni, nj] == P[k][si, sj] + 1) for (ni, nj) in neighbors(si, sj) ])
    minus_source = cp.sum([ (B[ni, nj] == k) & (P[k][ni, nj] == P[k][si, sj] - 1) for (ni, nj) in neighbors(si, sj) ])
    model += (plus_source == 1)
    model += (minus_source == 0)

    # For sink: exactly one neighbor with -1, none with +1
    plus_sink = cp.sum([ (B[ni, nj] == k) & (P[k][ni, nj] == P[k][ti, tj] + 1) for (ni, nj) in neighbors(ti, tj) ])
    minus_sink = cp.sum([ (B[ni, nj] == k) & (P[k][ni, nj] == P[k][ti, tj] - 1) for (ni, nj) in neighbors(ti, tj) ])
    model += (plus_sink == 0)
    model += (minus_sink == 1)

    # For non-terminal cells of color k: exactly one neighbor at +1 and one at -1
    for i in range(n):
        for j in range(m):
            if (i, j) == (si, sj) or (i, j) == (ti, tj):
                continue
            is_k = (B[i, j] == k)
            plus_cnt = cp.sum([ (B[ni, nj] == k) & (P[k][ni, nj] == P[k][i, j] + 1) for (ni, nj) in neighbors(i, j) ])
            minus_cnt = cp.sum([ (B[ni, nj] == k) & (P[k][ni, nj] == P[k][i, j] - 1) for (ni, nj) in neighbors(i, j) ])
            model += is_k.implies((plus_cnt == 1) & (minus_cnt == 1))

# Objective (none, just find a solution that satisfies all constraints)

# Solve and print
if model.solve():
    solution = {'B': B.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
