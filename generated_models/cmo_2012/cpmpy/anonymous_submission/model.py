from cpmpy import *
import json
import math

# Decision Variables
a = intvar(2012, 10000, name="a")  # a must be ≥2012
b = intvar(1, 10000, name="b")     # b must be positive
n = intvar(1, 10000, name="n")     # n must be positive
p = intvar(2, 10000, name="p")     # p must be prime

# Model
model = Model()

# Constraints
# a - b is prime
model += (a - b == p)

# a × b is perfect square n^2
model += (a * b == n * n)

# Proper primality check
model += (p >= 2)
max_divisor = int(math.sqrt(10000)) + 1
for d in range(2, max_divisor):
    model += (p % d != 0) | (p <= d)

# Objective: minimize a
model.minimize(a)

# Solve
model.solve()

# Print solution
solution = {
    "a": a.value(),
    "b": b.value(),
    "n": n.value(),
    "p": p.value()
}
print(json.dumps(solution))
# End of CPMPy script