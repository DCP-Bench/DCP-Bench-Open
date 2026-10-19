import json
import sys

import mip

data = json.load(open(sys.argv[1]))
n = data["n_nodes"]
edges = data["edges"]
K = n  # at most one colour per node

m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
m.verbose = 0
m.max_mip_gap = 0.0
m.max_mip_gap_abs = 0.0
# x[i][c] = 1 when node i gets colour c; w[c] = 1 when colour c is used
x = [[m.add_var(f"x_{i}_{c}", var_type=mip.BINARY) for c in range(K)] for i in range(n)]
w = [m.add_var(f"w_{c}", var_type=mip.BINARY) for c in range(K)]

# every node gets exactly one colour
for i in range(n):
    m += mip.xsum(x[i]) == 1

# a colour is used when some node has it
for i in range(n):
    for c in range(K):
        m += x[i][c] <= w[c]

# adjacent nodes get different colours
for a, b in edges:
    for c in range(K):
        m += x[a][c] + x[b][c] <= 1

# symmetry breaking: colours are used in index order
for c in range(K - 1):
    m += w[c] >= w[c + 1]

m.objective = mip.xsum(w)

status = m.optimize(max_seconds=300)
if status != mip.OptimizationStatus.OPTIMAL:
    raise SystemExit(f"Status: {status.name}")

raw = [next(c for c in range(K) if x[i][c].x > 0.5) for i in range(n)]
# renumber the used colours to 0..k-1
used = sorted(set(raw))
renumber = {c: k for k, c in enumerate(used)}
print(json.dumps({"colour": [renumber[c] for c in raw]}))
