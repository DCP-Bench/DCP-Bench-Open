
import cpmpy as cp
import json

n = 31
coins_per_line = 14

# Model definition
model = cp.Model()

# Decision Variables: x[i][j] = 1 if coin placed at row i, column j, else 0
x = cp.intvar(0, 1, shape=(n, n), name="x")

# Constraints
# 1. Each row has exactly 14 coins
for i in range(n):
    model += (cp.sum(x[i, :]) == coins_per_line)

# 2. Each column has exactly 14 coins
for j in range(n):
    model += (cp.sum(x[:, j]) == coins_per_line)

# 4. At most one coin per cell (already ensured by domain 0/1)

# Objective: minimize sum of squared horizontal distance from main diagonal
# distance for cell (i,j) is (i-j)^2
distances = [[(i - j) ** 2 for j in range(n)] for i in range(n)]
obj = cp.sum([x[i, j] * distances[i][j] for i in range(n) for j in range(n)])

model.minimize(obj)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist(), 'z': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
