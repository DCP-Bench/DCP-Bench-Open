
import cpmpy as cp
import json

# Data
n = 10  # Size of the chessboard and number of queens
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# queens[i] is the column (1..n) of the queen in row i (rows are 1..n)
queens = cp.intvar(1, n, shape=n, name="queens")

# Constraints
# 1) No two queens in same column
model += cp.AllDifferent(queens)

# 2) No two queens on the same diagonals:
# For queens at rows i and j (1-based), |queens[i]-queens[j]| != |i-j|
# Equivalent to AllDifferent of queens[i] + i and queens[i] - i
diag_plus  = [queens[i] + (i + 1) for i in range(n)]
diag_minus = [queens[i] - (i + 1) for i in range(n)]
model += cp.AllDifferent(*diag_plus)
model += cp.AllDifferent(*diag_minus)

# Solve and print
if model.solve():
    solution = {'queens': queens.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
