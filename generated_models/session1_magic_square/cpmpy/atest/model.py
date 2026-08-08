from cpmpy import *
import json

# Parameters
n = 4  # Size of the magic square

# Decision variables
square = intvar(1, n * n, shape=(n, n), name="square")

# Model
model = Model()

# All numbers from 1 to n^2 must be used exactly once
model += [AllDifferent(square.flatten())]

# Sum of each row must be equal to the magic constant
magic_constant = n * (n * n + 1) // 2
for i in range(n):
    model += [sum(square[i, :]) == magic_constant]

# Sum of each column must be equal to the magic constant
for j in range(n):
    model += [sum(square[:, j]) == magic_constant]

# Sum of the main diagonal must be equal to the magic constant
model += [sum(square[i, i] for i in range(n)) == magic_constant]

# Sum of the anti-diagonal must be equal to the magic constant
model += [sum(square[i, n - 1 - i] for i in range(n)) == magic_constant]

# Solve the model
model.solve()

# Print the solution
solution = {"square": square.value().tolist()}
print(json.dumps(solution))