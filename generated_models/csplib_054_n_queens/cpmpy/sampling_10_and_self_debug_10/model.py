
import cpmpy as cp
import json

# Data
n = 10
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# We represent the solution by an array 'queens' of length n,
# where queens[i] = row position of the queen in column i (0-based indexing)
queens = cp.intvar(0, n-1, shape=n, name="queens")

# Constraints
# 1) All queens must be in different rows
model += cp.AllDifferent(queens)

# 2) No two queens share the same diagonal
# For diagonals, the difference (row - column) and sum (row + column) must be all different
diag1 = [queens[i] + i for i in range(n)]
diag2 = [queens[i] - i for i in range(n)]
model += cp.AllDifferent(diag1)
model += cp.AllDifferent(diag2)

# Solve and print
if model.solve():
    # queens[i] is the row of the queen in column i
    solution = {'queens': [int(queens[i].value()) for i in range(n)]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
