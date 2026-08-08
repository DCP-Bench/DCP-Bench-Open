
import cpmpy as cp
import json

# Data
A = [81, 21, 79, 4, 29, 70, 28, 20, 14, 7]
n = len(A)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
in_S = cp.intvar(0, 1, shape=n, name="in_S")
in_T = cp.intvar(0, 1, shape=n, name="in_T")

# Constraints
# 1) Disjoint subsets: an element can't be in both S and T
for i in range(n):
    model += in_S[i] + in_T[i] <= 1

# 2) Non-empty subsets
model += cp.sum(in_S) >= 1
model += cp.sum(in_T) >= 1

# 3) Equal sums
model += cp.sum(in_S[i] * A[i] for i in range(n)) == cp.sum(in_T[i] * A[i] for i in range(n))

# Solve and print
if model.solve():
    solution = {
        'in_S': in_S.value().tolist(),
        'in_T': in_T.value().tolist()
    }
    print(json.dumps(solution))
else:
    print("No solution found.")
