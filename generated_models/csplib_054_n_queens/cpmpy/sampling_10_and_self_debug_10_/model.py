
import cpmpy as cp
import json

# Data
n = 10  # Size of the chessboard and number of queens
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# queens[i] = column (1..n) of the queen in row i (0-based index for rows)
queens = cp.intvar(1, n, shape=n, name="queens")

# Constraints
# 1) All queens are in different columns
model += cp.AllDifferent(queens)

# 2) No two queens share a diagonal:
# For each row i, the expressions queens[i] + i and queens[i] - i must all be different
diag1 = [queens[i] + i for i in range(n)]   # major diagonals
diag2 = [queens[i] - i for i in range(n)]   # minor diagonals
model += cp.AllDifferent(*diag1)
model += cp.AllDifferent(*diag2)

# Solve and print
if model.solve():
    solution = {'queens': queens.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
