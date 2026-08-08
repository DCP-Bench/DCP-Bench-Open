
import cpmpy as cp
import json

# Data
board = [[1, 0, 0, 2, 3],
         [0, 0, 0, 4, 0],
         [0, 0, 4, 0, 0],
         [0, 2, 3, 0, 5],
         [0, 1, 5, 0, 0]]

n = len(board)
m = len(board[0])
C = 5  # colors 1..5

# Model definition
model = cp.Model()

# Decision Variables
B = cp.intvar(1, C, shape=(n, m), name="B")  # board colors 1..5
# x[c,i,j] == 1 iff cell (i,j) has color c+1
x = cp.boolvar(shape=(C, n, m), name="x")

# Constraints

# Fix given endpoints in B
for i in range(n):
    for j in range(m):
        if board[i][j] != 0:
            model += (B[i, j] == board[i][j])

# Link x and B: x[c,i,j] == (B[i,j] == c+1)
for c in range(C):
    val = c + 1
    for i in range(n):
        for j in range(m):
            model += (x[c, i, j] == (B[i, j] == val))

# Each cell has exactly one color
for i in range(n):
    for j in range(m):
        model += cp.sum([x[c, i, j] for c in range(C)]) == 1

# Helper: neighbors (orthogonal)
def neighbors(i, j):
    for di, dj in ((-1,0),(1,0),(0,-1),(0,1)):
        ni, nj = i+di, j+dj
        if 0 <= ni < n and 0 <= nj < m:
            yield ni, nj

# Degree/connectivity constraints per color
for c in range(C):
    val = c + 1
    # Per-cell degree constraints
    for i in range(n):
        for j in range(m):
            neigh_vars = [x[c, ni, nj] for (ni, nj) in neighbors(i, j)]
            deg_ij = cp.sum(neigh_vars)  # number of same-color neighbors of cell (i,j)
            if board[i][j] == val:
                # This is a fixed endpoint for color val
                model += x[c, i, j] == 1
                model += deg_ij == 1
            else:
                # If this cell has color c -> must have degree 2 (internal node)
                model += x[c, i, j].implies(deg_ij == 2)

    # Connectivity/uniqueness constraint: ensure exactly one connected component per color
    # k = number of cells colored c
    k = cp.sum([x[c, i, j] for i in range(n) for j in range(m)])
    # sum_deg = sum over colored cells of their degree (i.e., count degrees only for cells that are colored)
    sum_deg = cp.sum([ x[c, i, j] * cp.sum([x[c, ni, nj] for (ni, nj) in neighbors(i, j)]) 
                       for i in range(n) for j in range(m) ])
    # For a single connected component (tree-like path between two endpoints), we must have:
    # sum_deg == 2 * (k - 1)  (this forces exactly one connected component; cycles are thereby prevented)
    model += sum_deg == 2 * (k - 1)

# Solve
if model.solve():
    solution = {'B': B.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
