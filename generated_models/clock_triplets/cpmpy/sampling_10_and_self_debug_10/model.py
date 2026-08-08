
import cpmpy as cp
import json

# Numbers on clock face: 1 to 12
n = 12
nums = list(range(1, n + 1))

# Model definition
model = cp.Model()

# Decision Variables
# x[i]: the number at position i on the clock, i=0..11, x[0] fixed to 12
x = cp.intvar(1, 12, shape=n, name="x")

# Constraints
# All numbers are distinct
model += cp.AllDifferent(x)

# The first number is fixed to 12
model += (x[0] == 12)

# For each triplet of adjacent numbers on the clock, sum <= 21
# The clock is circular, so indices wrap around modulo 12
for i in range(n):
    triplet_sum = x[i] + x[(i+1) % n] + x[(i+2) % n]
    model += (triplet_sum <= 21)

# No objective needed, just feasibility with the given max sum

if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
