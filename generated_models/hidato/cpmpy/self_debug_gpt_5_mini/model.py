
import cpmpy as cp
import json

# Data
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
R = len(puzzle)
C = len(puzzle[0])
N = R * C  # 144

# Model definition
model = cp.Model()

# Decision Variables
# Index 0 unused to make indexing by number easier: numbers 1..N
pr = cp.intvar(0, R-1, shape=N+1, name="pr")    # row of number v
pc = cp.intvar(0, C-1, shape=N+1, name="pc")    # col of number v
pidx = cp.intvar(0, N-1, shape=N+1, name="pidx")# cell index = row*C + col

# Constraints
# Link pidx with pr and pc: pidx[v] == pr[v]*C + pc[v]
for v in range(1, N+1):
    model += (pidx[v] == pr[v] * C + pc[v])

# All numbers occupy distinct cells
model += cp.AllDifferent([pidx[v] for v in range(1, N+1)])

# Fixed clues from puzzle
for r in range(R):
    for c in range(C):
        val = puzzle[r][c]
        if val != 0:
            # position of val is fixed to this cell
            model += (pidx[val] == r * C + c)

# Adjacency constraints: consecutive numbers must be in adjacent cells (including diagonals)
for v in range(1, N):
    # Chebyshev distance <= 1 and not the same cell
    model += (cp.Abs(pr[v] - pr[v+1]) <= 1)
    model += (cp.Abs(pc[v] - pc[v+1]) <= 1)
    # not both differences zero (i.e., not same cell)
    model += ((pr[v] != pr[v+1]) | (pc[v] != pc[v+1]))

# Solve
if model.solve():
    # build solved grid x as list of lists
    x = [[0 for _ in range(C)] for __ in range(R)]
    # place each number v at its solved coordinates
    for v in range(1, N+1):
        r = int(pr[v].value())
        c = int(pc[v].value())
        x[r][c] = int(v)
    solution = {'x': x}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
