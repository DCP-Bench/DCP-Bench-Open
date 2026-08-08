
import cpmpy as cp
import json
import numpy as np

# Data
n = 10  # Size of the grid (n x n)
c = 5   # Number of coins in each row and column
# End of data

# Model definition
model = cp.Model()

# Decision Variables: x[i,j] = 1 if there is a coin in cell (i,j), else 0
x = cp.boolvar(shape=(n, n), name="x")

# Precompute squared horizontal distances from main diagonal: (j - i)^2
dist_sq = np.array([[(j - i) ** 2 for j in range(n)] for i in range(n)], dtype=int)

# Constraints
# 1. Each row has exactly c coins
for i in range(n):
    model += cp.sum(x[i, :]) == c

# 2. Each column has exactly c coins
for j in range(n):
    model += cp.sum(x[:, j]) == c

# 4. At most one coin per cell is enforced by boolean domain of x

# Objective: minimize sum of squared horizontal distances of occupied cells
obj_terms = []
for i in range(n):
    for j in range(n):
        # weight times the boolean variable
        obj_terms.append(int(dist_sq[i, j]) * x[i, j])
model.minimize(cp.sum(obj_terms))

# Solve and print
if model.solve():
    # x.value() is a numpy array of booleans; convert to ints 0/1
    x_vals = x.value().astype(int).tolist()
    z_val = int(model.objective_value())
    solution = {'x': x_vals, 'z': z_val}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
