
import cpmpy as cp
import json

# Data
n = 27
m = 5

# Model definition
model = cp.Model()

# Decision Variables
# s: the series (s0, s1, ..., sn, sn+1)
# Each si is an integer variable >= 0
s = cp.intvar(0, 1000, shape=n+2, name="s")  # upper bound large enough to allow counts

# Constraints
# 1) There are si occurrences of i in S for each i = 0 to n
# This means count of value i in s is exactly s[i]
for i in range(n+1):
    model += cp.Count(s, i) == s[i]

# 2) sn+1 = m (the last element of s equals m)
model += s[n+1] == m

# Additionally, the series must be non-empty
# sum of all si should be >= 1
model += cp.sum(s) >= 1

# Solve and print
if model.solve():
    solution = {'s': s.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
