
import cpmpy as cp
import json

# Data
n = 27
m = 5
# End of data

# Model definition
model = cp.Model()

# Decision Variables: s0..s_{n+1} (length n+2)
s = cp.intvar(0, n+1, shape=n+2, name="s")

# Constraints:
# For each i in 0..n+1, the number of occurrences of value i in s is equal to s[i].
for i in range(n+2):
    model += (cp.Count(s, i) == s[i])

# fix s[n+1] = m
model += (s[n+1] == m)

# Solve and print
if model.solve():
    solution = {'s': s.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
