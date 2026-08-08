
import cpmpy as cp
import json

# Data (optional)
n = 27
m = 5
# End of data

N = n + 2  # length of the series S

# Model definition
model = cp.Model()

# Decision Variables
# s[0..N-1], values can be between 0 and N (counts cannot exceed N)
s = cp.intvar(0, N, shape=N, name="s")

# Constraints

# 1) For each i in 0..n, the number of occurrences of value i in S equals s[i]
vals = list(range(n + 1))  # values 0..n
model += cp.GlobalCardinalityCount(s, vals, s[0:n+1])

# 2) s[n+1] = m
model += (s[n+1] == m)

# Helpful pruning: total number of values in 0..n cannot exceed the sequence length
model += (cp.sum(s[0:n+1]) <= N)

# Objective (none)

# Solve and print
if model.solve():
    solution = {'s': s.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
