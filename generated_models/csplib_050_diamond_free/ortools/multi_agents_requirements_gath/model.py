import json
from itertools import combinations
from ortools.sat.python import cp_model

# --------------------------------------------------
# Input data (immutable, must not be changed)
# --------------------------------------------------
N = 10  # Number of vertices in the graph

# --------------------------------------------------
# CP-SAT model
# --------------------------------------------------
model = cp_model.CpModel()

# 1. Edge variables – one Boolean per unordered pair (i<j)
edge = {}
for i in range(N):
    for j in range(i + 1, N):
        edge[(i, j)] = model.NewBoolVar(f"e_{i}_{j}")

# Helper to access the unique variable for an edge {u,v}
get_edge = lambda u, v: edge[(u, v)] if u < v else edge[(v, u)]

# 2. Degree variables d_i ∈ {3,6,9}
allowed_degrees = [3, 6, 9]
max_deg = max(allowed_degrees)

deg = []
for i in range(N):
    d = model.NewIntVarFromDomain(cp_model.Domain.FromValues(allowed_degrees), f"deg_{i}")
    # Definition of degree: sum of incident edges
    incident_sum = sum(get_edge(i, j) for j in range(N) if j != i)
    model.Add(d == incident_sum)
    deg.append(d)

# 3. Non-increasing degree sequence (symmetry breaking)
for i in range(N - 1):
    model.Add(deg[i] >= deg[i + 1])

# 4. Sum of degrees divisible by 12  ⇒  there exists k s.t. Σ d_i = 12·k
# Maximum possible sum is N*max_deg = 90, minimum 30.
max_k = (N * max_deg) // 12  # 7 (since 12*7 = 84 < 90 < 12*8)
aux_k = model.NewIntVar(0, max_k, "k")
model.Add(sum(deg) == 12 * aux_k)

# 5. Diamond-free constraint – for every quartet, at most 4 edges inside it
for quartet in combinations(range(N), 4):
    quartet_edges = [get_edge(u, v) for u, v in combinations(quartet, 2)]  # 6 edges
    model.Add(sum(quartet_edges) <= 4)

# --------------------------------------------------
# Solve (feasibility)
# --------------------------------------------------
solver = cp_model.CpSolver()
# Feel free to tweak limits – here we keep a reasonable cap for demonstration.
solver.parameters.max_time_in_seconds = 120
solver.parameters.num_search_workers = 8

status = solver.Solve(model)

# --------------------------------------------------
# Output
# --------------------------------------------------
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    matrix = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(i + 1, N):
            val = solver.Value(edge[(i, j)])
            matrix[i][j] = val
            matrix[j][i] = val
    # Diagonal already 0
    print(json.dumps({"matrix": matrix}))
else:
    # No feasible graph found within limits – return empty matrix for compliance
    print(json.dumps({"matrix": []}))
