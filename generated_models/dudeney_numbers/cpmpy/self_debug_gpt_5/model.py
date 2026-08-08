
import cpmpy as cp
import json

# Data (optional)
# max number of digits
n = 6
# End of data

# Helper to compute integer cube root
def int_cuberoot(x):
    r = 0
    while (r + 1) ** 3 <= x:
        r += 1
    return r

# Derived data
max_number = 10**n - 1
weights = [10**(n - 1 - i) for i in range(n)]
root_upper_bound = min(9 * n, int_cuberoot(max_number))
cubes = [i**3 for i in range(root_upper_bound + 1)]

# Model definition
model = cp.Model()

# Decision Variables
digits = cp.intvar(0, 9, shape=n, name="digits")
number = cp.intvar(0, max_number, name="number")
root = cp.intvar(0, root_upper_bound, name="root")

# Constraints
# number is represented by its decimal digits
model += (number == cp.sum([digits[i] * weights[i] for i in range(n)]))
# number greater than 1
model += (number > 1)
# number is a perfect cube, and root is its cube root
model += (cp.Element(cubes, root) == number)
# sum of digits equals the cube root
model += (cp.sum(digits) == root)

# Solve and print
if model.solve():
    solution = {'number': int(number.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
