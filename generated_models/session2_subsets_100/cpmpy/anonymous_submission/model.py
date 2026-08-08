# Import libraries
from cpmpy import *
import json

# Given set A
A = [81, 21, 79, 4, 29, 70, 28, 20, 14, 7]

# Decision Variables
in_S = intvar(0, 1, shape=10, name="in_S")  # Binary: 1 if element is in S
in_T = intvar(0, 1, shape=10, name="in_T")  # Binary: 1 if element is in T

# Model
model = Model()

# Constraint: S and T are non-empty
model += sum(in_S) >= 1
model += sum(in_T) >= 1

# Constraint: S and T are disjoint (no common elements)
for i in range(10):
    model += (in_S[i] + in_T[i]) <= 1

# Constraint: sum of elements in S equals sum of elements in T
sum_S = sum(A[i] * in_S[i] for i in range(10))
sum_T = sum(A[i] * in_T[i] for i in range(10))
model += sum_S == sum_T

# Solve
model.solve()

# Print solution with boolean conversion
solution = {
    "in_S": [bool(val) for val in in_S.value().tolist()],
    "in_T": [bool(val) for val in in_T.value().tolist()]
}
print(json.dumps(solution))
# End of CPMPy script