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

# no objective: any feasible placement is optimal
status = m.optimize(max_seconds=60)
if status == mip.OptimizationStatus.OPTIMAL:
    queens = [next(c for c in range(n) if q[r][c].x > 0.5) for r in range(n)]
    print(json.dumps({"queens": queens}))
elif status == mip.OptimizationStatus.INFEASIBLE:
    print(json.dumps({"status": "unsatisfiable"}))
else:
    raise SystemExit(f"Status: {status.name}")
