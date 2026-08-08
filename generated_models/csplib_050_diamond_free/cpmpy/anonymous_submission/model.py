# Import libraries
from cpmpy import *
import json

# Parameters
N = 10  # Number of vertices in the graph

# Decision Variables
matrix = boolvar(shape=(N,N), name="matrix")  # Adjacency matrix

# Model
model = Model()

# Constraint: no self-loops (diagonal is 0)
for i in range(N):
    model += ~matrix[i,i]

# Constraint: undirected graph (symmetric matrix)
for i in range(N):
    for j in range(i+1, N):
        model += matrix[i,j] == matrix[j,i]

# Compute degrees
degrees = [sum(matrix[i,:]) for i in range(N)]

# Constraint: degree of each vertex > 0 and mod 3
for i in range(N):
    model += degrees[i] > 0
    model += degrees[i] % 3 == 0

# Constraint: degrees in non-increasing order
for i in range(N-1):
    model += degrees[i] >= degrees[i+1]

# Constraint: sum of degrees mod 12
model += sum(degrees) % 12 == 0

# Constraint: diamond-free (no 4 vertices with 5 or more edges)
for i in range(N):
    for j in range(i+1, N):
        for k in range(j+1, N):
            for l in range(k+1, N):
                # Count all possible edges between these 4 vertices
                edge_count = sum([
                    matrix[i,j], matrix[i,k], matrix[i,l],
                    matrix[j,k], matrix[j,l], matrix[k,l]
                ])
                model += edge_count <= 4

# Solve
model.solve()

# Print solution
solution = {
    "matrix": matrix.value().tolist()
}
print(json.dumps(solution))