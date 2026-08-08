
import cpmpy as cp
import json

# Data
n = 12  # The number N
# End of data

# Model definition
model = cp.Model()

# Decision Variables: x[i] = 1 if (i+1) is in A, 0 if in B
x = cp.intvar(0, 1, shape=n, name="x")

# Precomputed totals
total_sum = n * (n + 1) // 2
total_sum_sq = n * (n + 1) * (2 * n + 1) // 6

half_count = n // 2
half_sum = total_sum // 2
half_sum_sq = total_sum_sq // 2

# Constraints
model += cp.sum(x) == half_count
model += cp.sum([x[i] * (i + 1) for i in range(n)]) == half_sum
model += cp.sum([x[i] * (i + 1) * (i + 1) for i in range(n)]) == half_sum_sq

# Symmetry breaking: enforce that 1 is in A (safe because A/B are symmetric)
model += x[0] == 1

# Solve and print
if model.solve():
    xv = x.value().tolist()
    A = [i + 1 for i, val in enumerate(xv) if int(val) == 1]
    B = [i + 1 for i, val in enumerate(xv) if int(val) == 0]
    solution = {'A': A, 'B': B}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
