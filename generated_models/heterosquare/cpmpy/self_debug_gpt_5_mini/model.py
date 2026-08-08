
import cpmpy as cp
import json

# Data
n = 5
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(1, n*n, shape=(n, n), name="x")

# Constraints
# All entries are distinct and in 1..n^2
model += cp.AllDifferent(x)

# Row sums and column sums
row_sums = [cp.sum(x[i, :]) for i in range(n)]
col_sums = [cp.sum(x[:, j]) for j in range(n)]

# Diagonal sums
diag1 = cp.sum([x[i, i] for i in range(n)])
diag2 = cp.sum([x[i, n-1-i] for i in range(n)])

# All sums (rows, columns, diagonals) must be pairwise different
all_sums = row_sums + col_sums + [diag1, diag2]
model += cp.AllDifferent(all_sums)

# Symmetry-breaking: fix one cell to reduce search (without loss of generality)
model += (x[0, 0] == 1)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
