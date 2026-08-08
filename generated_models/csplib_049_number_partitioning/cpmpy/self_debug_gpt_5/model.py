
import cpmpy as cp
import json

# Data (optional)
n = 12  # The number N
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# x[i] = 1 if (i+1) is in set A, 0 otherwise (then it's in set B)
x = cp.intvar(0, 1, shape=n, name="x")

# Precompute constants
numbers = list(range(1, n+1))
total_sum = n * (n + 1) // 2
total_sq = sum(i * i for i in numbers)

# Expressions for sums
sum_A = cp.sum([(i + 1) * x[i] for i in range(n)])
sum2_A = cp.sum([(i + 1) * (i + 1) * x[i] for i in range(n)])

# Constraints
# Equal cardinality: |A| = |B| -> 2*|A| = n (handles odd n as unsat)
model += (2 * cp.sum(x) == n)

# Equal sum: sum(A) = sum(B) -> 2*sum(A) = total_sum
model += (2 * sum_A == total_sum)

# Equal sum of squares: sum(i^2 in A) = sum(i^2 in B) -> 2*sum2_A = total_sq
model += (2 * sum2_A == total_sq)

# Solve and print
if model.solve():
    x_vals = x.value().tolist()
    A = [i + 1 for i, v in enumerate(x_vals) if v == 1]
    B = [i + 1 for i, v in enumerate(x_vals) if v == 0]
    solution = {'A': A, 'B': B}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
