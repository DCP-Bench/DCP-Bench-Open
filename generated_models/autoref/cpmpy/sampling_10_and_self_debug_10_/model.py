
import cpmpy as cp
import json

# Data
n = 27
m = 5
# End of data

# Model definition
model = cp.Model()

# Decision Variables: s[0..n+1]
length = n + 2
s = cp.intvar(0, length, shape=length, name="s")

# Constraints
# 1) For each i in 0..n, there are s[i] occurrences of value i in the sequence s
for i in range(0, n + 1):
    model += (cp.Count(s, i) == s[i])

# 2) s[n+1] == m
model += (s[n + 1] == m)

# Solve and print
if model.solve():
    solution = {'s': s.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
