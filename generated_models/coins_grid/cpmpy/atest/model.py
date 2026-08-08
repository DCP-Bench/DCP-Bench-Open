from cpmpy import *
import json

# Parameters
n = 31  # Size of the grid
coins_per_row = 14  # Number of coins per row
coins_per_col = 14  # Number of coins per column

# Decision variables
x = boolvar(shape=(n, n), name="x")  # x[i][j] = 1 if a coin is placed in cell (i, j), 0 otherwise
z = intvar(0, 1000000, name="z")  # Sum of the quadratic horizontal distance from the main diagonal

# Model
model = Model()

# 1. In each row exactly 14 coins must be placed
for i in range(n):
    model += [sum(x[i, :]) == coins_per_row]

# 2. In each column exactly 14 coins must be placed
for j in range(n):
    model += [sum(x[:, j]) == coins_per_col]

# 3. The sum of the quadratic horizontal distance from the main diagonal of all cells containing a coin must be as small as possible
# The quadratic horizontal distance from the main diagonal for cell (i, j) is (i - j)^2
# We minimize the sum of these distances for all cells with a coin
model += [z == sum((i - j) ** 2 * x[i, j] for i in range(n) for j in range(n))]

# 4. In each cell at most one coin can be placed
# This is already enforced by x being a boolean variable

# Minimize the sum of the quadratic horizontal distance
model.minimize(z)

# Solve the model
model.solve()

# Print the solution
solution = {"x": (x.value()).astype(int).tolist(), "z": z.value()}
print(json.dumps(solution))