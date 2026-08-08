
import cpmpy as cp
import json
import itertools

# Data
N = 10
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# Adjacency matrix: boolean variables (0/1)
A = cp.boolvar(shape=(N, N), name="A")

# Degree variables
# Domain 0..N-1 but we will restrict to {3,6,9} (positive and multiples of 3)
d = cp.intvar(0, N-1, shape=N, name="d")

# Constraints
# Simple graph: no self-loops and symmetry
for i in range(N):
    model += (A[i, i] == 0)
    for j in range(i + 1, N):
        model += (A[i, j] == A[j, i])

# Degrees equal row sums
for i in range(N):
    model += (cp.sum([A[i, j] for j in range(N)]) == d[i])

# Each degree is > 0 and multiple of 3. For N=10 possible values are 3,6,9
for i in range(N):
    model += cp.InDomain(d[i], [3, 6, 9])

# Non-increasing degree sequence: d0 >= d1 >= ... >= d_{N-1}
for i in range(N - 1):
    model += (d[i] >= d[i + 1])

# Sum of degrees is divisible by 12
model += (cp.sum(d) % 12 == 0)

# Diamond-free: for every set of 4 vertices, at most 4 edges among them
# For each 4-combination, sum of the 6 possible edges <= 4
for (i, j, k, l) in itertools.combinations(range(N), 4):
    edges = [
        A[i, j], A[i, k], A[i, l],
        A[j, k], A[j, l],
        A[k, l]
    ]
    model += (cp.sum(edges) <= 4)

# Solve and print
if model.solve():
    # Convert boolean matrix to list of lists of 0/1 integers
    matrix_vals = A.value().tolist()
    # Ensure integers (cpmpy returns ints for boolvar values, but wrap to be safe)
    matrix_int = [[int(x) for x in row] for row in matrix_vals]
    solution = {'matrix': matrix_int}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
