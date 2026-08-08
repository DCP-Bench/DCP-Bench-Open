
import cpmpy as cp
import json
import itertools

# Data
N = 10  # Number of vertices in the graph
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# adjacency matrix: 0/1 variables
matrix = cp.intvar(0, 1, shape=(N, N), name="matrix")
# degrees for each vertex
deg = cp.intvar(0, N-1, shape=N, name="deg")
# sum of degrees (for modulo constraint)
sumdeg = cp.intvar(0, N*(N-1), name="sumdeg")

# Constraints

# Simple undirected graph: no self-loops and symmetry
for i in range(N):
    model += (matrix[i, i] == 0)
    for j in range(i+1, N):
        model += (matrix[i, j] == matrix[j, i])

# Degrees equal row sums
for i in range(N):
    model += (deg[i] == cp.sum(matrix[i, :]))

# Each degree > 0 and divisible by 3.
# For N=10, possible positive degrees divisible by 3 are {3,6,9}
for i in range(N):
    model += ((deg[i] == 3) | (deg[i] == 6) | (deg[i] == 9))

# Degrees are non-increasing: d_i >= d_{i+1}
for i in range(N-1):
    model += (deg[i] >= deg[i+1])

# Sum of degrees is divisible by 12
model += (sumdeg == cp.sum(deg))
model += (sumdeg % 12 == 0)

# Diamond-free: for every set of 4 vertices, the number of edges among them <= 4
# For a set of four vertices, there are 6 possible edges (pairs). Sum of those <= 4.
for quad in itertools.combinations(range(N), 4):
    pairs = list(itertools.combinations(quad, 2))
    model += (cp.sum([matrix[i, j] for (i, j) in pairs]) <= 4)

# Solve and print
if model.solve():
    solution = {'matrix': matrix.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
