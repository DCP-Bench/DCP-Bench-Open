
import cpmpy as cp
import json

# Data
n = 8  # Size of the Costas array
# End of data

# Model definition
model = cp.Model()

# Decision Variables: costas is the permutation X_1..X_n (1-based values)
costas = cp.intvar(1, n, shape=n, name="costas")

# Constraints
# 1) permutation: all values in costas are different (one mark per column)
model += cp.AllDifferent(costas)

# 2) difference triangle: for each lag l = 1..n-1, the differences X_i - X_{i+l} (i=1..n-l) are all different
# We'll create difference rows for each l and enforce the equality and all-different constraint.
for l in range(1, n):
    row_len = n - l
    D = cp.intvar(-(n-1), (n-1), shape=row_len)  # differences can be negative
    # link differences to permutation variables
    for i in range(row_len):
        model += (D[i] == costas[i] - costas[i + l])
    # each row must have all different differences
    model += cp.AllDifferent(D)

# Optional symmetry breaking: fix one orientation to reduce symmetrical solutions
# (e.g., first element less than last element)
model += (costas[0] < costas[-1])

# Solve and print
if model.solve():
    solution = {'costas': costas.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
