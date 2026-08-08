
import cpmpy as cp
import json
import math

# Data (optional)
N_MIN = 1
N_MAX = 10000

# Precompute squares for constraints
max_a = math.isqrt(N_MAX + 1)  # for x+1 = a^2
squares1 = [i * i for i in range(1, max_a + 1)]

max_h_plus_1 = (N_MAX // 2) + 1  # for (x//2)+1 = b^2
max_b = math.isqrt(max_h_plus_1)
squares2 = [i * i for i in range(1, max_b + 1)]
# End of data

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(N_MIN, N_MAX, name="x")
h = cp.intvar(N_MIN // 2, N_MAX // 2, name="h")  # x = 2*h, h in [0..5000] but x>=1 => h>=0
k1 = cp.intvar(0, len(squares1) - 1, name="k1")
k2 = cp.intvar(0, len(squares2) - 1, name="k2")

# Constraints
# - x is even, modeled via x = 2*h
model += (2 * h == x)
# - x != 48 (find another number)
model += (x != 48)
# - x+1 is a perfect square
model += (cp.Element(squares1, k1) == x + 1)
# - (x//2)+1 is a perfect square -> since x=2*h, this is h+1
model += (cp.Element(squares2, k2) == h + 1)

# Objective (optional)
# None, just find any solution

# Solve and print
if model.solve():
    solution = {'peculiar': int(x.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
