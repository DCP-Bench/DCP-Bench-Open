from cpmpy import *
import json

# Parameters
n = 10  # Size of the chessboard and number of queens

# Decision variables
# queens[i] represents the row of the queen in column i
queens = intvar(0, n - 1, shape=n, name="queens")

# Model
model = Model()

# All queens must be in different rows
model += [AllDifferent(queens)]

# No two queens can be on the same diagonal
# Use AllDifferent to ensure all \ diagonals (queens[i] - i) are unique
model += [AllDifferent(queens - arange(n))]
# Use AllDifferent to ensure all / diagonals (queens[i] + i) are unique
model += [AllDifferent(queens + arange(n))]

# Solve the model
model.solve()

# Print the solution
solution = {"queens": queens.value().tolist()}
print(json.dumps(solution))