
import cpmpy as cp
import json

# Data
A = [81, 21, 79, 4, 29, 70, 28, 20, 14, 7]
n = len(A)

# Model definition
model = cp.Model()

# Decision variables: binary variables indicating membership in S and T
in_S = cp.boolvar(shape=n, name="in_S")
in_T = cp.boolvar(shape=n, name="in_T")

# Constraints
# 1) S and T are disjoint: no element can be in both sets
model += [in_S[i] + in_T[i] <= 1 for i in range(n)]

# 2) Both S and T are non-empty
model += cp.sum(in_S) >= 1
model += cp.sum(in_T) >= 1

# 3) Sum of elements in S equals sum of elements in T
sum_S = cp.sum([in_S[i] * A[i] for i in range(n)])
sum_T = cp.sum([in_T[i] * A[i] for i in range(n)])
model += (sum_S == sum_T)

# No objective, just find any feasible solution
if model.solve():
    solution = {
        'in_S': [int(x) for x in in_S.value().tolist()],
        'in_T': [int(x) for x in in_T.value().tolist()]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
