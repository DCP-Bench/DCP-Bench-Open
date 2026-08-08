# Import libraries
from cpmpy import *
import json

# Decision Variables
s = intvar(0, 9, name="s")  # S
e = intvar(0, 9, name="e")  # E
n = intvar(0, 9, name="n")  # N
d = intvar(0, 9, name="d")  # D
m = intvar(0, 9, name="m")  # M
o = intvar(0, 9, name="o")  # O
r = intvar(0, 9, name="r")  # R
y = intvar(0, 9, name="y")  # Y

# Model
model = Model()

# Constraint: All letters must have distinct values
model += AllDifferent([s, e, n, d, m, o, r, y])

# Constraint: First letters cannot be zero
model += s != 0
model += m != 0

# Constraint: SEND + MORE = MONEY
send = 1000*s + 100*e + 10*n + d
more = 1000*m + 100*o + 10*r + e
money = 10000*m + 1000*o + 100*n + 10*e + y
model += (send + more) == money

# Solve
model.solve()

# Print solution
solution = {
    "s": s.value(),
    "e": e.value(),
    "n": n.value(),
    "d": d.value(),
    "m": m.value(),
    "o": o.value(),
    "r": r.value(),
    "y": y.value()
}
print(json.dumps(solution))
# End of CPMPy script