
import cpmpy as cp
import json

n = 27
m = 5

# Variables: s is an array of 28 variables (indices 0 to 27)
s = cp.intvar(0, 29, shape=28, name="s")

model = cp.Model()

# Constraint 1: Sum of s must be 29 (total elements excluding the last fixed m)
model += cp.sum(s) == 29

# Constraint 2: For each i in 0..n, count of i in s plus 1 (if i == m) must equal s[i]
for i in range(n + 1):
    count_in_s = cp.Count(s, i)
    if i == m:
        total_count = count_in_s + 1
    else:
        total_count = count_in_s
    model += (total_count == s[i])

# Solve the model
if model.solve():
    # The full series S is the variables s followed by m
    series = s.value().tolist() + [m]
    solution = {'s': series}
    print(json.dumps(solution))
else:
    print("No solution found.")
