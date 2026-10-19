# N-queens: place n queens on an n x n board so that no two attack each other, and count every
# placement. One binary per square; 1 means a queen stands there.
# Enumeration: after each placement, a no-good cut over the square binaries (the only outputs)
# forbids it, and the loop stops at the first infeasible model. Zero solutions: the loop body never
# runs, the count is 0 and nothing is printed after it. One solution: the count is 1.
# Output: the count, then the first placement as a plain list of rows (1 = queen).
import mip

n = 6

m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
m.verbose = 0
m.max_mip_gap = 0.0
m.max_mip_gap_abs = 0.0
q = [[m.add_var(f"q_{r}_{c}", var_type=mip.BINARY) for c in range(n)] for r in range(n)]

# every row holds exactly one queen
for r in range(n):
    m += mip.xsum(q[r]) == 1

# every column holds at most one queen
for c in range(n):
    m += mip.xsum(q[r][c] for r in range(n)) <= 1

# every diagonal running down-right (constant r - c) holds at most one queen
for d in range(-(n - 1), n):
    m += mip.xsum(q[r][r - d] for r in range(n) if 0 <= r - d < n) <= 1

# every diagonal running down-left (constant r + c) holds at most one queen
for s in range(2 * n - 1):
    m += mip.xsum(q[r][s - r] for r in range(n) if 0 <= s - r < n) <= 1

# no objective: this is a satisfaction problem
placements = []
while True:
    status = m.optimize(max_seconds=60)
    if status == mip.OptimizationStatus.INFEASIBLE:
        break
    if status != mip.OptimizationStatus.OPTIMAL:
        raise SystemExit(f"Status: {status.name}")
    board = [[round(q[r][c].x) for c in range(n)] for r in range(n)]
    placements.append(board)
    # no-good: at least one square changes from this placement
    m += mip.xsum((1 - q[r][c]) if board[r][c] == 1 else q[r][c]
                  for r in range(n) for c in range(n)) >= 1

print("Solutions:", len(placements))
if placements:
    print("First placement (rows of 0/1, 1 = queen):", placements[0])
