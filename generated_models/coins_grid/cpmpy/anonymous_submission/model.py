# Import libraries
from cpmpy import *
import json

# Parameters
n = 31  # Size of the grid (31x31)
coins_per_row = 14  # Coins per row
coins_per_col = 14  # Coins per column

# Decision Variables
x = intvar(0, 1, shape=(n, n), name="x")  # Whether a coin is placed in each cell (0 or 1)
z = intvar(0, n*n*n, name="z")  # Sum of quadratic horizontal distances

# Model
model = Model()

# Constraints
# 1. Exactly 14 coins per row
for i in range(n):
    model += sum(x[i, :]) == coins_per_row

# 2. Exactly 14 coins per column
for j in range(n):
    model += sum(x[:, j]) == coins_per_col

# 3. Sum of quadratic horizontal distances from main diagonal
model += z == sum((i - j)**2 * x[i, j] for i in range(n) for j in range(n))

# 4. At most one coin per cell (enforced by 0-1 variables)

# Objective: minimize z
model.minimize(z)

# Solve
model.solve()

# Print solution
solution = {
    "x": x.value().tolist(),
    "z": z.value()
}
print(json.dumps(solution))
# End of CPMPy script