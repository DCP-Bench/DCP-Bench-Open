
import cpmpy as cp
import json
from math import isqrt

# Data (precompute Pythagorean triples up to sum 1000)
max_sum = 1000
triples = []
for a_val in range(1, max_sum - 1):
    for b_val in range(a_val + 1, max_sum - a_val):
        # Early pruning: minimal c is b_val+1, so if a+b+(b+1) > max_sum, break
        if a_val + b_val + (b_val + 1) > max_sum:
            break
        c2 = a_val * a_val + b_val * b_val
        c_val = isqrt(c2)
        if c_val * c_val == c2 and c_val > b_val and a_val + b_val + c_val <= max_sum:
            triples.append([a_val, b_val, c_val])
# End of data

# Model definition
model = cp.Model()

# Decision Variables
a = cp.intvar(1, max_sum, name="a")
b = cp.intvar(1, max_sum, name="b")
c = cp.intvar(1, max_sum, name="c")

# Constraints
model += (a < b)
model += (b < c)
model += (a + b + c == max_sum)
model += cp.Table([a, b, c], triples)

# Objective (none)

# Solve and print
if model.solve():
    solution = {'a': int(a.value()), 'b': int(b.value()), 'c': int(c.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
