
import cpmpy as cp
import json

# Data
n = 4
magic_sum = n * (n * n + 1) // 2  # 34 for n=4

# Model definition
model = cp.Model()

# Decision Variables
square = cp.intvar(1, n*n, shape=(n, n), name="square")

# Constraints
# All cells must be different
model += [cp.AllDifferent(square)]

# Row sums and column sums
for i in range(n):
    model += cp.sum(square[i, :]) == magic_sum
for j in range(n):
    model += cp.sum(square[:, j]) == magic_sum

# Diagonal sums
model += cp.sum([square[i, i] for i in range(n)]) == magic_sum
model += cp.sum([square[i, n-1-i] for i in range(n)]) == magic_sum

# Solve and print
if model.solve():
    solution = {'square': square.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
