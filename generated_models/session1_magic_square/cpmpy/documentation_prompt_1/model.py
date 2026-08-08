
import cpmpy as cp
import json

n = 4
magic_sum = n * (n**2 + 1) // 2

# Model definition
model = cp.Model()

# Decision Variables: n x n grid with values from 1 to n^2
square = cp.intvar(1, n**2, shape=(n, n), name="square")

# Constraints
# All values must be different
model += cp.AllDifferent(square)

# Each row sums to magic_sum
for i in range(n):
    model += cp.sum(square[i, :]) == magic_sum

# Each column sums to magic_sum
for j in range(n):
    model += cp.sum(square[:, j]) == magic_sum

# Main diagonal sums to magic_sum
model += cp.sum([square[i, i] for i in range(n)]) == magic_sum

# Secondary diagonal sums to magic_sum
model += cp.sum([square[i, n - 1 - i] for i in range(n)]) == magic_sum

# Solve and print
if model.solve():
    solution = {'square': square.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
