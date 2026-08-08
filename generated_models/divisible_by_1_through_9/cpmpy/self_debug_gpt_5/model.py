
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# Digits 0..9 used exactly once to form the 10-digit number
d = cp.intvar(0, 9, shape=10, name="d")
# Prefix values p[i] is the integer formed by the first i+1 digits
p = [cp.intvar(0, 10**(i+1)-1, name=f"p_{i+1}") for i in range(10)]
# Multipliers for divisibility constraints: p[i] = (i+1) * k[i]
k = [cp.intvar(0, (10**(i+1)-1)//(i+1), name=f"k_{i+1}") for i in range(10)]

# Constraints
# All digits different and first digit non-zero (to ensure a true 10-digit number)
model += cp.AllDifferent(d)
model += (d[0] != 0)

# Recurrence to build prefix numbers from digits
model += (p[0] == d[0])
for i in range(1, 10):
    model += (p[i] == 10 * p[i-1] + d[i])

# Divisibility constraints: first n digits divisible by n (n from 1 to 10)
for i in range(10):
    n = i + 1
    model += (p[i] == n * k[i])

# Optional implied constraint for speed: full number divisible by 10 -> last digit 0
model += (d[9] == 0)

# Solve and print
if model.solve():
    number = int(p[9].value())
    solution = {'number': number}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
