
import cpmpy as cp
import json
import numpy as np

# Data
n = 5
N = n * n
all_vals_sum = N * (N + 1) // 2  # sum of 1..N = 325

# Bounds for sums (tighten domains)
min_row_sum = sum(range(1, n + 1))  # 1+2+...+n = 15
max_row_sum = sum(range(N - n + 1, N + 1))  # (N-n+1)+...+N = 115

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(1, N, shape=(n, n), name="x")

# Sums
row_sums = cp.intvar(min_row_sum, max_row_sum, shape=n, name="row_sums")
col_sums = cp.intvar(min_row_sum, max_row_sum, shape=n, name="col_sums")
diag_sums = cp.intvar(min_row_sum, max_row_sum, shape=2, name="diag_sums")

# Constraints
# All numbers 1..N exactly once
model += cp.AllDifferent(x)

# Link sums
for i in range(n):
    model += (row_sums[i] == cp.sum(x[i, :]))
for j in range(n):
    model += (col_sums[j] == cp.sum(x[:, j]))

model += (diag_sums[0] == cp.sum([x[i, i] for i in range(n)]))
model += (diag_sums[1] == cp.sum([x[i, n - 1 - i] for i in range(n)]))

# All row, column, and diagonal sums are all different
model += cp.AllDifferent(list(row_sums) + list(col_sums) + list(diag_sums))

# Redundant helpful constraints
model += (cp.sum(row_sums) == all_vals_sum)
model += (cp.sum(col_sums) == all_vals_sum)

# Symmetry breaking to speed up search (safe)
# Sort row sums and column sums to break row/column permutation symmetry
model += cp.IncreasingStrict(row_sums)
model += cp.IncreasingStrict(col_sums)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
