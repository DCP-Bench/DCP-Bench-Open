
import cpmpy as cp
import json
import math

# Data
existing = [1, 3, 8, 120]
UB = 100000  # upper bound for search (sufficient to find the minimal solution)
max_square = 120 * UB + 1
max_t = int(math.isqrt(max_square)) + 1
squares = [i * i for i in range(1, max_t + 1)]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
number = cp.intvar(0, UB, name="number")

# Constraints: For each a in existing, a*number + 1 is a perfect square
for a in existing:
    model += cp.Table([a * number + 1], [[s] for s in squares])

# Objective: find the smallest such number
model.minimize(number)

# Solve and print
if model.solve():
    solution = {'number': int(number.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
