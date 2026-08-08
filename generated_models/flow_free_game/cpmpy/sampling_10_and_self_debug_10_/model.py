
import cpmpy as cp
import json

# Data
board = [[1, 0, 0, 2, 3],
         [0, 0, 0, 4, 0],
         [0, 0, 4, 0, 0],
         [0, 2, 3, 0, 5],
         [0, 1, 5, 0, 0]]
n = 5
colors = 5  # colors numbered 1..5
maxcells = n * n

# Model definition
model = cp.Model()

# Decision Variables
B = cp.intvar(1, colors, shape=(n, n), name="B")  # board colors to output

# X[c,i,j] is True iff cell (i,j) has color c+1
X = cp.boolvar(shape=(colors, n, n), name="X")

# dist[c,i,j]: distance along the path from the chosen root endpoint (0..maxcells-1)
dist = cp.intvar(0, maxcells - 1, shape=(colors, n, n), name="dist")

# succ[c,i,j,k]: for cell (i,j), k in [0..3] corresponds to neighbor directions
# order of directions: 0=up,1=right,2=down,3=left
succ = cp.boolvar(shape=(colors, n, n, 4), name="succ")

# Helper: neighbor directions
dirs = [(-1, 0), (0, 1), (1, 0), (0, -1)]
opp = [2, 3, 0, 1]  # opposite direction index

# Add basic channeling between B and X, and fix pre-filled cells
for i in range(n):
    for j in range(n):
        if board[i][j] != 0:
            # fixed prefilled value
            model += (B[i, j] == board[i][j])
        # Channel X variables with B
        for c in range(colors):
            model += (X[c, i, j] == (B[i, j] == (c + 1)))

# For succ variables, set them to 0 when neighbor doesn't exist, and basic linking
for c in range(colors):
    for i in range(n):
        for j in range(n):
            for k, (di, dj) in enumerate(dirs):
                ni, nj = i + di, j + dj
                s = succ[c, i, j, k]
                if not (0 <= ni < n and 0 <= nj < n):
                    # invalid neighbor: no successor allowed
                    model += (s == 0)
                else:
                    # successor implies both source and target cells have the color
                    model += (s <= X[c, i, j])
                    model += (s <= X[c, ni, nj])
                    # if s is true then dist[ni,nj] == dist[i,j] + 1
                    model += s.implies(dist[c, ni, nj] == dist[c, i, j] + 1)

# Identify endpoints (the two given cells) for each color, choose the first as root, second as sink
endpoints = {}
for c in range(1, colors + 1):
    pts = []
    for i in range(n):
        for j in range(n):
            if board[i][j] == c:
                pts.append((i, j))
    if len(pts) != 2:
        raise ValueError(f"Color {c} does not have exactly 2 endpoints in the input.")
    endpoints[c] = (pts[0], pts[1])

# Constraints to enforce single non-branching path connecting the two endpoints for each color
for c in range(colors):
    col = c + 1
    (r_i, r_j), (s_i, s_j) = endpoints[col]
    for i in range(n):
        for j in range(n):
            # compute prev_sum: number of incoming succs from neighbors into (i,j)
            incoming = []
            outgoing = []
            for k, (di, dj) in enumerate(dirs):
                ni, nj = i + di, j + dj
                if 0 <= ni < n and 0 <= nj < n:
                    incoming.append(succ[c, ni, nj, opp[k]])
                    outgoing.append(succ[c, i, j, k])
            prev_sum = cp.sum(incoming)
            next_sum = cp.sum(outgoing)

            # If this cell is the chosen root for this color
            if (i, j) == (r_i, r_j):
                model += (X[c, i, j] == 1)  # must be the color
                model += (dist[c, i, j] == 0)
                model += (prev_sum == 0)
                model += (next_sum == 1)
            # If this cell is the sink endpoint
            elif (i, j) == (s_i, s_j):
                model += (X[c, i, j] == 1)
                model += (prev_sum == 1)
                model += (next_sum == 0)
            else:
                # For other cells: if they are of this color they must have exactly one incoming and one outgoing
                model += X[c, i, j].implies(prev_sum == 1)
                model += X[c, i, j].implies(next_sum == 1)
                # If not of this color, there should be no incoming or outgoing succ edges (these are enforced by succ <= X constraints)

# Solve and print
if model.solve():
    solution = {'B': B.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
