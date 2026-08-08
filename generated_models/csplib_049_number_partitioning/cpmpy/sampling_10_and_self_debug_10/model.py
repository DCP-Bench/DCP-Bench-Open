
import cpmpy as cp
import json

# Data
n = 12

# Model definition
model = cp.Model()

# Decision Variables
# x[i] = 0 if i+1 in A, 1 if i+1 in B
x = cp.intvar(0, 1, shape=n, name="x")

# Constraints
# A and B have the same cardinality
model += (cp.sum(x) == n // 2)

# Sum of numbers in A = sum of numbers in B
# sum of numbers in B = sum of numbers in 1..n - sum of numbers in A
# sum of numbers in A = sum_{i | x[i]==0} (i+1)
# sum of numbers in B = sum_{i | x[i]==1} (i+1)
# So sum of A = sum of B = total_sum/2
total_sum = n * (n + 1) // 2
model += (cp.sum([(1 - x[i]) * (i + 1) for i in range(n)]) == total_sum // 2)

# Sum of squares of numbers in A = sum of squares of numbers in B
total_sum_sq = sum((i + 1) ** 2 for i in range(n))
model += (cp.sum([(1 - x[i]) * (i + 1) ** 2 for i in range(n)]) == total_sum_sq // 2)

# Domain feasibility check (no solution if n < 8 or n % 4 != 0)
if n < 8 or n % 4 != 0:
    print("No solution found.")
else:
    # Solve and print
    if model.solve():
        A = [i + 1 for i in range(n) if x[i].value() == 0]
        B = [i + 1 for i in range(n) if x[i].value() == 1]
        solution = {'A': A, 'B': B}
        print(json.dumps(solution, indent=4))
    else:
        print("No solution found.")
