
import cpmpy as cp
import json

# Data
n = 4
M = n * (n*n + 1) // 2  # magic constant = 34 for n=4

# Model definition
model = cp.Model()

# Decision Variables: n x n square with values 1..n^2
square = cp.intvar(1, n*n, shape=(n, n), name="square")

# Constraints
# All cells are different and within 1..n^2 (domain already enforces range)
model += cp.AllDifferent(square)

# Each row sums to M
for i in range(n):
    model += cp.sum(square[i, :]) == M

# Each column sums to M
for j in range(n):
    model += cp.sum(square[:, j]) == M

# Main diagonal sums to M
model += cp.sum([square[i, i] for i in range(n)]) == M

# Anti-diagonal sums to M
model += cp.sum([square[i, n-1-i] for i in range(n)]) == M

# Solve and print
if model.solve():
    solution = {'square': square.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
