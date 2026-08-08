
import cpmpy as cp
import json

# Data
n = 6
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# digits: most-significant first, allow leading zeros
digits = cp.intvar(0, 9, shape=n, name="digits")
# cube root r (must be integer and > 1)
r_min = 2
r_max = int((10**n - 1) ** (1/3))  # largest integer whose cube fits in n digits
r = cp.intvar(r_min, r_max, name="r")
# the number itself
number = cp.intvar(2, 10**n - 1, name="number")

# Precompute powers of 10 for positional values
pow10 = [10 ** (n - 1 - i) for i in range(n)]

# Constraints
# number is formed by the digits
model += (number == cp.sum([digits[i] * pow10[i] for i in range(n)]))
# number is a perfect cube: number == r^3
model += (number == r * r * r)
# sum of digits equals the cube root
model += (cp.sum(digits) == r)
# ensure number > 1 (already ensured by domains) and fits in n digits (domain does)

# Solve and print
if model.solve():
    solution = {'number': int(number.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
