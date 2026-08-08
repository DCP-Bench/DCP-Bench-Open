
import cpmpy as cp
import json
import math

# Model definition
model = cp.Model()

# Parameters
MAX_S = 1000  # sufficient upper bound to find smallest a >= 2012
P_MAX = 2 * MAX_S + 1
MAXD = int(math.isqrt(P_MAX))

# Decision Variables
s = cp.intvar(1, MAX_S, name="s")
a = cp.intvar(0, (MAX_S + 1) * (MAX_S + 1), name="a")
b = cp.intvar(0, MAX_S * MAX_S, name="b")
n = cp.intvar(0, MAX_S * (MAX_S + 1), name="n")
p = cp.intvar(0, P_MAX, name="p")

# Constraints
# a = (s+1)^2, b = s^2, n = s*(s+1), p = a - b
model += (a == (s + 1) * (s + 1))
model += (b == s * s)
model += (n == s * (s + 1))
model += (p == a - b)

# a >= 2012 and b > 0, p >= 2
model += (a >= 2012)
model += (b >= 1)
model += (p >= 2)

# p is prime: for all 2 <= d <= floor(sqrt(P_MAX)), enforce p == d or p % d != 0
for d in range(2, MAXD + 1):
    model += (p == d) | (p % d != 0)

# Objective: minimize a
model.minimize(a)

# Solve and print
if model.solve():
    solution = {
        'a': int(a.value()),
        'b': int(b.value()),
        'n': int(n.value()),
        'p': int(p.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
