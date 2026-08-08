
import cpmpy as cp
import json

# Data
n = 27
m = 5
# End of data

# Model definition
model = cp.Model()

# Decision Variables: s0..s_{n+1} (length n+2)
# Each s[i] is an integer; counts can be as large as n+2, so keep that upper bound.
s = cp.intvar(0, n+2, shape=n+2, name="s")

# Constraints:
# For each i in 0..n, the number of occurrences of value i in S is equal to s[i].
for i in range(n+1):  # 0..n
    model += (cp.Count(s, i) == s[i])

# fix s[n+1] = m
model += (s[n+1] == m)

# The sum of all count variables s[0..n] must equal the length of S (n+2).
# (Do NOT include s[n+1] in this sum because s[n+1] is a value, not a count.)
model += (cp.sum(s[:n+1]) == n+2)

# Solve and print
if model.solve():
    solution = {'s': s.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
