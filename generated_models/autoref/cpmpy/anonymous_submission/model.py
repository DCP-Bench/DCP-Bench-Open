# Import libraries
from cpmpy import *
import json

# Parameters
n = 27
m = 5

# Decision Variables
# The series S has length n+2 (from s0 to sn+1)
s = intvar(0, n+2, shape=n+2, name="s")  # Series S

# Model
model = Model()

# Constraint 1: sn+1 = m
model += (s[-1] == m)

# Constraint 2: For each i from 0 to n, there are si occurrences of i in S
for i in range(n+1):
    model += (sum(s == i) == s[i])

# Solve
model.solve()

# Print solution
solution = {
    "s": s.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script