
import cpmpy as cp
import json
import numpy as np

# Data (optional)
n = 10  # Size of the grid (n x n)
c = 5   # Number of coins in each row and column
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.boolvar(shape=(n, n), name="x")  # 1 if a coin is placed at (i,j), else 0
max_sq = (n - 1) ** 2
z = cp.intvar(0, n * c * max_sq, name="z")  # total quadratic horizontal distance

# Constraints
# 1) Row sums equal to c
for i in range(n):
    model += (cp.sum(x[i, :]) == c)

# 2) Column sums equal to c
for j in range(n):
    model += (cp.sum(x[:, j]) == c)

# 3) Objective definition: sum of squared horizontal distances from the main diagonal
cost_terms = [x[i, j] * ((j - i) ** 2) for i in range(n) for j in range(n)]
model += (z == cp.sum(cost_terms))

# Objective (minimize total distance)
model.minimize(z)

# Solve and print
if model.solve():
    solution = {
        'x': np.array(x.value(), dtype=int).tolist(),
        'z': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
