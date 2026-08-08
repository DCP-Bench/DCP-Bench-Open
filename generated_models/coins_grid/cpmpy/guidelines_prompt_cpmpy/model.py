
import cpmpy as cp
import json

# Data
n = 31  # size of the board
k = 14  # coins per row/column
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# x[i,j] = 1 if we place a coin in cell (i,j), else 0
x = cp.intvar(0, 1, shape=(n, n), name="x")
# z is the total sum of squared horizontal distances from the main diagonal
# maximum possible (worst‐case) distance^2 is 30^2=900, times 31*31 ≈ 864900, so we give a safe upper bound
z = cp.intvar(0, 1000000, name="z")

# Constraints

# 1. Each row must have exactly k coins
for i in range(n):
    model += cp.sum(x[i, j] for j in range(n)) == k

# 2. Each column must have exactly k coins
for j in range(n):
    model += cp.sum(x[i, j] for i in range(n)) == k

# 3. Define z as the sum of squared distances from the main diagonal
expr = cp.sum((i - j) ** 2 * x[i, j] for i in range(n) for j in range(n))
model += (z == expr)

# Objective: minimize z
model.minimize(z)

# Solve and print
if model.solve():
    solution = {
        'x': x.value().tolist(),
        'z': int(z.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
