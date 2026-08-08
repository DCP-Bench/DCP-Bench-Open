
import cpmpy as cp
import json
import numpy as np

# Data (optional)
n = 10  # Size of the chessboard and number of queens
# End of data

# Model definition
model = cp.Model()

# Decision Variables
queens = cp.intvar(1, n, shape=n, name="queens")

# Constraints
rows = np.arange(n)
model += [
    cp.AllDifferent(queens),          # Different columns
    cp.AllDifferent(queens + rows),   # Different major diagonals
    cp.AllDifferent(queens - rows)    # Different minor diagonals
]

# Objective (optional)
# None, just find a feasible solution

# Solve and print
if model.solve():
    solution = {'queens': queens.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
