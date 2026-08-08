
import cpmpy as cp
import json

# Data
n = 9  # Order of the Steiner Triple System
# End of data

# Number of triples
m = n * (n - 1) // 6  # should be integer for valid n (here 12)

# Model definition
model = cp.Model()

# Decision Variables: boolean matrix X of shape (m, n)
# X[i, j] == 1 iff element (j+1) is in triple i
X = cp.boolvar(shape=(m, n), name="x")

# Constraints

# Each triple contains exactly 3 elements
for i in range(m):
    model += (cp.sum(X[i, :]) == 3)

# Each element occurs in exactly (n-1)/2 triples
rep_per_element = (n - 1) // 2
for j in range(n):
    model += (cp.sum(X[:, j]) == rep_per_element)

# Every pair of distinct elements occurs together in exactly one triple
for a in range(n):
    for b in range(a + 1, n):
        # sum over triples of the conjunction that both elements a and b are present
        model += (cp.sum([ (X[i, a] & X[i, b]) for i in range(m)]) == 1)

# Symmetry breaking: order the triples lexicographically to reduce equivalent solutions
model += cp.LexChainLessEq([X[i, :] for i in range(m)])

# Solve and print
if model.solve():
    # Convert boolean matrix to 0/1 integers
    raw = X.value().tolist()
    matrix_int = [[int(cell) for cell in row] for row in raw]
    # Print under key 'sets' as requested by the problem description
    solution = {'sets': matrix_int}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
