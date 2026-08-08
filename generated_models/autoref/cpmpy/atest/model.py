from cpmpy import *
import json

# Input data
n = 27  # Given integer n
m = 5   # Given integer m

# Parameters
length_S = n + 2  # The series S has length n + 2

# Decision variables
s = intvar(0, 100, shape=length_S, name="s")  # The series S

# Model
model = Model()

# Constraint (1): There are s[i] occurrences of i in S for each i from 0 to n
for i in range(n + 1):
    model += [sum((s == i)) == s[i]]

# Constraint (2): s[n+1] = m
model += [s[n + 1] == m]

# Solve the model
model.solve()

# Print the solution
solution = {"s": s.value().tolist()}
print(json.dumps(solution))