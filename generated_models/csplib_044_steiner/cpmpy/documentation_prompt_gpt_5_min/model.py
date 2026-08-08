
import cpmpy as cp
import json
import numpy as np

# Data
n = 9  # Order of the Steiner Triple System
m = n * (n - 1) // 6  # number of triples

# Model definition
model = cp.Model()

# Decision Variables
# x[i, j] = 1 if element j (1..n) is in triple i (0..m-1)
x = cp.boolvar(shape=(m, n), name="x")

# Auxiliary integer encoding of each row to forbid duplicate triples
max_row_val = (1 << n) - 1
row_val = cp.intvar(0, max_row_val, shape=m, name="row_val")

# Constraints

# Each triple has exactly 3 distinct elements
for i in range(m):
    model += (cp.sum(x[i, :]) == 3)

# Each element occurs in exactly (n-1)/2 triples (balance property of STS)
r = (n - 1) // 2
for j in range(n):
    model += (cp.sum(x[:, j]) == r)

# Each pair of distinct elements appears together in exactly one triple
for a in range(n):
    for b in range(a + 1, n):
        # sum over triples of (x[t,a] AND x[t,b]) == 1
        model += (cp.sum(x[:, a] & x[:, b]) == 1)

# No duplicate triples: encode each row as a unique integer (bitmask)
for i in range(m):
    model += (row_val[i] == cp.sum([x[i, j] * (1 << j) for j in range(n)]))
model += cp.AllDifferent(row_val)

# (Optional) Symmetry breaking: enforce rows in non-decreasing order of their integer encoding
for i in range(m - 1):
    model += (row_val[i] <= row_val[i + 1])

# Solve and print
if model.solve():
    # Convert boolean matrix to 0/1 integers
    x_vals = x.value().astype(int).tolist()
    solution = {'x': x_vals}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
