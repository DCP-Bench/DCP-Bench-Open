
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
    # Convert boolean arrays to integer lists (0/1)
    solution = {
        'in_S': s.value().astype(int).tolist(),
        'in_T': t.value().astype(int).tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
