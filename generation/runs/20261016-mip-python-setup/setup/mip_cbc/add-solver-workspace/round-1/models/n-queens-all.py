import json
import sys

import mip

n = json.load(open(sys.argv[1]))["n"]

m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
m.verbose = 0
m.max_mip_gap = 0.0
m.max_mip_gap_abs = 0.0
# one binary per square: 1 when a queen stands there
q = [[m.add_var(f"q_{r}_{c}", var_type=mip.BINARY) for c in range(n)] for r in range(n)]

# every row holds exactly one queen
for r in range(n):
    m += mip.xsum(q[r]) == 1

# every column holds at most one queen
for c in range(n):
    m += mip.xsum(q[r][c] for r in range(n)) <= 1

# every diagonal running down-right (constant c - r) holds at most one queen
for d in range(-(n - 1), n):
    m += mip.xsum(q[r][r - d] for r in range(n) if 0 <= r - d < n) <= 1

# every diagonal running down-left (constant r + c) holds at most one queen
for s in range(2 * n - 1):
    m += mip.xsum(q[r][s - r] for r in range(n) if 0 <= s - r < n) <= 1

# enumerate: after each placement, a no-good cut over the square binaries forbids it
count = 0
while True:
    status = m.optimize(max_seconds=60)
    if status == mip.OptimizationStatus.INFEASIBLE:
        break
    if status != mip.OptimizationStatus.OPTIMAL:
        raise SystemExit(f"Status: {status.name}")
    board = [[round(q[r][c].x) for c in range(n)] for r in range(n)]
    queens = [row.index(1) for row in board]
    print(json.dumps({"queens": queens}), flush=True)
    count += 1
    m += mip.xsum((1 - q[r][c]) if board[r][c] == 1 else q[r][c]
                  for r in range(n) for c in range(n)) >= 1

if count == 0:
    print(json.dumps({"status": "unsatisfiable"}))
