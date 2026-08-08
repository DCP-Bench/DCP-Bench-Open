
import cpmpy as cp
import json

# Data
A = [81, 21, 79, 4, 29, 70, 28, 20, 14, 7]

# Model definition
model = cp.Model()

# Decision Variables
s = cp.boolvar(shape=10, name='s')  # 1 if element is in S
t = cp.boolvar(shape=10, name='t')  # 1 if element is in T

# Constraints
for i in range(10):
    model += (s[i] + t[i] <= 1)  # Disjoint subsets

sum_S = cp.sum(s * A)
sum_T = cp.sum(t * A)
model += (sum_S == sum_T)  # Equal sums
model += (cp.sum(s) >= 1)  # S is non-empty
model += (cp.sum(t) >= 1)  # T is non-empty

# Solve and print
if model.solve():
    solution = {
        'in_S': s.value().tolist(),
        'in_T': t.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
