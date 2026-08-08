
import cpmpy as cp
import json

N = 10  # Number of vertices in the graph

# Model definition
model = cp.Model()

# Decision Variables
# adjacency matrix: symmetric, 0 diagonal
adj = cp.intvar(0, 1, shape=(N, N), name="adj")
# degrees (to be sorted non-increasingly)
deg = cp.intvar(1, N-1, shape=N, name="deg")  # degree > 0, max N-1 (max edges per vertex)

# Constraints
# 1) Symmetry and no loops
for i in range(N):
    model += (adj[i, i] == 0)
    for j in range(i+1, N):
        model += (adj[i, j] == adj[j, i])

# 2) Degree definition: deg[i] = sum of adj[i,:]
for i in range(N):
    model += (deg[i] == cp.sum(adj[i, :]))

# 3) Degree sequence non-increasing
for i in range(N-1):
    model += (deg[i] >= deg[i+1])

# 4) Degrees > 0 and degree mod 3 == 0
for i in range(N):
    model += (deg[i] > 0)
    model += (deg[i] % 3 == 0)

# 5) Sum of degrees mod 12 == 0
model += (cp.sum(deg) % 12 == 0)

# 6) Diamond-free constraint:
# For every set of 4 vertices, the number of edges between them is at most 4
# To enforce this, for each 4-subset of vertices, sum edges between those vertices <= 4
# There are C(N,4) subsets; for N=10, 210 subsets, acceptable to enumerate

from itertools import combinations

quad_subsets = list(combinations(range(N), 4))
for subset in quad_subsets:
    # sum edges among these 4 vertices
    edges_in_quad = []
    for i in range(4):
        for j in range(i+1, 4):
            edges_in_quad.append(adj[subset[i], subset[j]])
    model += (cp.sum(edges_in_quad) <= 4)

# Solve and print
if model.solve():
    # Print adjacency matrix as list of lists of ints
    matrix = adj.value().tolist()
    solution = {'matrix': matrix}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
