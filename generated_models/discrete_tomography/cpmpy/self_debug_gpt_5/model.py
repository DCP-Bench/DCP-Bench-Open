
import cpmpy as cp
import json

# Data (optional)
row_sums = [0, 0, 8, 2, 6, 4, 5, 3, 7, 0, 0]  # Each number represents the number of 1s in the row
col_sums = [0, 0, 7, 1, 6, 3, 4, 5, 2, 7, 0, 0]  # Each number represents the number of 1s in the column
# End of data

# Model definition
model = cp.Model()

# Dimensions
n_rows = len(row_sums)
n_cols = len(col_sums)

# Decision Variables
matrix = cp.intvar(0, 1, shape=(n_rows, n_cols), name="matrix")

# Constraints
# Row sums
model += [cp.sum(matrix[i, :]) == row_sums[i] for i in range(n_rows)]
# Column sums
model += [cp.sum(matrix[:, j]) == col_sums[j] for j in range(n_cols)]

# Objective (optional)
# No objective, just find any feasible solution

# Solve and print
if model.solve():
    solution = {'matrix': matrix.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
