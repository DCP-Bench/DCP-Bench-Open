
import cpmpy as cp
import json

# Data
n = 31
coins_per_row = 14
coins_per_col = 14

# Model definition
model = cp.Model()

# Decision Variables
# x[i,j] = 1 if coin placed at row i, col j; 0 otherwise
x = cp.intvar(0, 1, shape=(n, n), name="x")

# Constraints
# Each row has exactly coins_per_row coins
for i in range(n):
    model += (cp.sum(x[i, :]) == coins_per_row)

# Each column has exactly coins_per_col coins
for j in range(n):
    model += (cp.sum(x[:, j]) == coins_per_col)

# Objective: minimize sum of squared horizontal distances from main diagonal
# horizontal distance = abs(j - i)
# sum over i,j of x[i,j] * (j - i)^2
distance_expr = cp.sum([x[i, j] * (j - i) ** 2 for i in range(n) for j in range(n)])
model.minimize(distance_expr)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist(), 'z': int(distance_expr.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
