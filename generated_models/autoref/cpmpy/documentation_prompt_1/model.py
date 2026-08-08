
import cpmpy as cp
import json

# Data
n = 27
m = 5
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# s is the series S = (s0, s1, ..., sn, sn+1)
# s[i] for i in [0..n] is the count of i in S
# s[n+1] = m (given)
s = cp.intvar(0, 1000, shape=n+2, name="s")  # upper bound 1000 is arbitrary large enough

# Constraints
# 1) s[i] occurrences of i in S for i in [0..n]
# This means for each i in [0..n], s[i] = count of i in S
# The count of i in S is s[i], so s[i] = s[i] trivially holds.
# But the key is that the length of S = sum of all s[i] for i in [0..n+1]
# and the counts must be consistent.

# The series S has length L = sum of s[i] for i in [0..n+1]
# The counts s[i] for i in [0..n] must be equal to the number of times i appears in S,
# which is s[i] itself, so this is consistent.

# The problem is a self-referential count vector: s[i] = number of times i appears in s[0..n]
# and s[n+1] = m given.

# So the key constraint is:
# For each i in [0..n], s[i] = count of i in s[0..n]
# s[n+1] = m

# Implement count constraints:
for i in range(n+1):
    model += (cp.Count(s[:n+1], i) == s[i])

# s[n+1] = m
model += (s[n+1] == m)

# The series S must be non-empty finite series
# So sum of s[i] for i in [0..n+1] > 0
model += (cp.sum(s) > 0)

# Solve and print
if model.solve():
    solution = {'s': s.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
