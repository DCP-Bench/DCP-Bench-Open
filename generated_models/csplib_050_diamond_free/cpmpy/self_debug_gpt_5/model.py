
import cpmpy as cp
import json
from itertools import combinations

# Data (optional)
N = 10  # Number of vertices in the graph
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# Adjacency matrix of the graph (boolean, symmetric, zero diagonal)
matrix = cp.boolvar(shape=(N, N), name="matrix")

# Degree of each vertex
deg = cp.intvar(0, N-1, shape=N, name="deg")

# Helper variables to enforce deg[i] % 3 == 0 and deg[i] > 0 (i.e., deg[i] = 3 * m[i], m[i] >= 1)
max_m = (N - 1) // 3
m = cp.intvar(1, max_m if max_m >= 1 else 1, shape=N, name="m")

# Constraints

# Simple undirected graph: no loops, symmetric adjacency
for i in range(N):
    model += (matrix[i, i] == 0)
for i in range(N):
    for j in range(i+1, N):
        model += (matrix[i, j] == matrix[j, i])

# Degree definition and divisibility by 3 (and > 0 via m >= 1)
for i in range(N):
    model += (deg[i] == cp.sum(matrix[i, :]))
    model += (deg[i] == 3 * m[i])
    model += (deg[i] >= 1)

# Non-increasing degree sequence: d_i >= d_{i+1}
model += cp.Decreasing(deg)

# Sum of degrees is divisible by 12: sum(deg) == 12 * t
sum_deg = cp.sum(deg)
t_min = (3 * N + 11) // 12  # minimal t given deg[i] >= 3 for all i
t_max = (N * (N - 1)) // 12  # safe upper bound
t = cp.intvar(max(1, t_min), max(t_min, t_max), name="t")
model += (sum_deg == 12 * t)

# Diamond-free constraint:
# For every 4-vertex subset S, the number of edges among S is at most 4
# That is, sum_{i<j in S} matrix[i,j] <= 4
for i, j, k, l in combinations(range(N), 4):
    model += (matrix[i, j] + matrix[i, k] + matrix[i, l] +
              matrix[j, k] + matrix[j, l] + matrix[k, l] <= 4)

# Objective (optional)
# No objective, we seek any feasible solution

# Solve and print
if model.solve():
    mat_bool = matrix.value().tolist()
    mat_int = [[int(b) for b in row] for row in mat_bool]
    solution = {'matrix': mat_int}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
