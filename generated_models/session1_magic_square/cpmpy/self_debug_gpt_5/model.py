
import cpmpy as cp
import json
import numpy as np

# Data
n = 4
magic_sum = n * (n*n + 1) // 2  # n(n^2+1)/2
# End of data

# Model definition
model = cp.Model()

# Decision Variables
square = cp.intvar(1, n*n, shape=(n, n), name="square")

# Constraints
# All numbers are different
model += cp.AllDifferent(square.flatten())

# Row sums
for i in range(n):
    model += (cp.sum(square[i, :]) == magic_sum)

# Column sums
for j in range(n):
    model += (cp.sum(square[:, j]) == magic_sum)

# Main diagonal sum
model += (cp.sum([square[i, i] for i in range(n)]) == magic_sum)

# Anti-diagonal sum
model += (cp.sum([square[i, n - 1 - i] for i in range(n)]) == magic_sum)

# Objective (none, satisfaction problem)

# Solve and print
if model.solve():
    solution = {'square': square.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
