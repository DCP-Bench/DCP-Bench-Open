
import cpmpy as cp
import json

# Data
n = 4
m = n * (n * n + 1) // 2  # magic constant, here 34

# Model definition
model = cp.Model()

# Decision Variables: n x n square with values 1..n^2
x = cp.intvar(1, n*n, shape=(n, n), name="x")

# Constraints
# All different
model += cp.AllDifferent(x)

# Row sums and column sums equal to magic constant m
for i in range(n):
    model += cp.sum(x[i, :]) == m
for j in range(n):
    model += cp.sum(x[:, j]) == m

# Diagonals
model += cp.sum([x[i, i] for i in range(n)]) == m
model += cp.sum([x[i, n-1-i] for i in range(n)]) == m

# Optional symmetry-breaking (helps solver): fix one cell to reduce symmetric solutions
# This is not required, but speeds up solving.
model += x[0, 0] < x[0, n-1]

# Solve and print
if model.solve():
    solution = {'square': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
