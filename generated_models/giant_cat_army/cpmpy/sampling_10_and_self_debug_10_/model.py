
import cpmpy as cp
import json
import math

# Data
n = 24  # length of sequence

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(0, 60, shape=n, name="x")  # sequence x[0]..x[23]
pos2 = cp.intvar(0, n - 1, name="pos2")
pos10 = cp.intvar(0, n - 1, name="pos10")
# We know 14 must be at the last position
# (but we'll still enforce pos ordering with pos14 = n-1)

# Constraints
model += (x[0] == 0)          # start with 0
model += (x[n - 1] == 14)     # end with 14
model += cp.AllDifferent(x)   # all elements distinct

# Build allowed transition table according to operations: +5, +7, sqrt (integer)
allowed = []
for v in range(0, 61):
    # +5
    if v + 5 <= 60:
        allowed.append([v, v + 5])
    # +7
    if v + 7 <= 60:
        allowed.append([v, v + 7])
    # sqrt if v is a perfect square (and sqrt is integer)
    s = int(math.isqrt(v))
    if s * s == v:
        allowed.append([v, s])

# Enforce that each consecutive pair (x[i-1], x[i]) is in allowed transitions
for i in range(1, n):
    model += cp.Table([x[i - 1], x[i]], allowed)

# Ensure values 2, 10, 14 appear in that order (14 is at the end)
# Use element constraints to bind positions of 2 and 10
model += cp.Element(x, pos2) == 2
model += cp.Element(x, pos10) == 10
# Order: pos2 < pos10 < last index
model += pos2 < pos10
model += pos10 < (n - 1)

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
