from cpmpy import *
import json
from itertools import combinations

# Parameters
N = 10  # Number of vertices in the graph

# Decision variables
matrix = boolvar(shape=(N, N), name="matrix")

# Model
model = Model()

# Ensure the matrix is symmetric (undirected graph)
for i in range(N):
    for j in range(i + 1, N):
        model += [matrix[i, j] == matrix[j, i]]

# Ensure no self-loops
for i in range(N):
    model += [matrix[i, i] == 0]

# Compute the degree of each vertex
degrees = [sum(matrix[i, :]) for i in range(N)]

# Degrees must be greater than 0
model += [degrees[i] > 0 for i in range(N)]

# Degrees must be modulo 3
for i in range(N):
    k = intvar(0, N, name=f"k_{i}")
    model += [degrees[i] == 3 * k]

# Degrees must be in non-increasing order
for i in range(N - 1):
    model += [degrees[i] >= degrees[i + 1]]

# Sum of degrees must be modulo 12
sum_degrees = sum(degrees)
k_sum = intvar(0, N * N, name="k_sum")
model += [sum_degrees == 12 * k_sum]

# Ensure the graph is diamond-free
# A diamond is a set of 4 vertices with at least 5 edges among them
# So, for any subset of 4 vertices, the number of edges must be <= 4
for subset in combinations(range(N), 4):
    # Count the number of edges among the subset
    edge_count = sum(matrix[i, j] for i in subset for j in subset if i < j)
    model += [edge_count <= 4]

# Solve the model
model.solve()

# Print the solution
solution = {"matrix": matrix.value().tolist()}
print(json.dumps(solution))