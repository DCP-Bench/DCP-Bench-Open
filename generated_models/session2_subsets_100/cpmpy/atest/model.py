from cpmpy import *
import json

# Given set A
A = [81, 21, 79, 4, 29, 70, 28, 20, 14, 7]

# Decision variables
# in_S[i] = 1 if A[i] is in subset S, else 0
# in_T[i] = 1 if A[i] is in subset T, else 0
in_S = boolvar(shape=len(A), name="in_S")
in_T = boolvar(shape=len(A), name="in_T")

# Model
model = Model()

# S and T are disjoint: for each element, it can be in S or T, but not both
model += [in_S[i] + in_T[i] <= 1 for i in range(len(A))]

# S and T are non-empty
model += [sum(in_S) >= 1]
model += [sum(in_T) >= 1]

# Sum of elements in S equals sum of elements in T
model += [sum([in_S[i] * A[i] for i in range(len(A))]) == sum([in_T[i] * A[i] for i in range(len(A))])]

# Solve the model
model.solve()

# Print the solution
solution = {
    "in_S": in_S.value().tolist(),
    "in_T": in_T.value().tolist()
}
print(json.dumps(solution))