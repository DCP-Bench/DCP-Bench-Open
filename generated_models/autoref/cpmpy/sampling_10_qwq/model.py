
import cpmpy as cp
import json

# Input data
n = 27
m = 5

# Decision Variables: s_0 to s_n (n+1 variables)
s_vars = cp.intvar(0, n+2, shape=(n+1), name="s")

model = cp.Model()

# Constraints for each i from 0 to n
for i in range(n + 1):
    add_m = 1 if (m == i) else 0
    count_i = cp.Count(s_vars, i)
    model += (count_i + add_m == s_vars[i])

# Sum constraint: sum(s_vars) must equal (n+2) minus adjustment for m exceeding n
total_sum = (n + 2) - (1 if m > n else 0)
model += (cp.sum(s_vars) == total_sum)

# Solve and print
if model.solve():
    s_list = s_vars.value().tolist()
    s_full = s_list + [m]
    solution = {'s': s_full}
    print(json.dumps(solution))
else:
    print("No solution found.")
