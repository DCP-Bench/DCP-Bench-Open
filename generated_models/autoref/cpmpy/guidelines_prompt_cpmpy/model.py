
import cpmpy as cp
import json

# Data
n = 27
m = 5
# End of data

# Model definition
model = cp.Model()

# Decision Variables: s[0] through s[n+1]
# Each element of the series S can range from 0 to n+1
s = cp.intvar(0, n+1, shape=n+2, name="s")

# Constraints

# 1) For each i in 0..n, the number of occurrences of i in S equals s[i]
for i in range(n+1):
    model += (cp.sum([s[j] == i for j in range(n+2)]) == s[i])

# 2) sn+1 = m
model += (s[n+1] == m)

# Solve and print
if model.solve():
    solution = {'s': s.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
