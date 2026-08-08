from cpmpy import *
import json

# Decision variables
s = intvar(0, 9, name="s")
e = intvar(0, 9, name="e")
n = intvar(0, 9, name="n")
d = intvar(0, 9, name="d")
m = intvar(0, 9, name="m")
o = intvar(0, 9, name="o")
r = intvar(0, 9, name="r")
y = intvar(0, 9, name="y")

# Model
model = Model()

# All letters must be assigned unique digits
model += [AllDifferent([s, e, n, d, m, o, r, y])]

# First letters of each word cannot be zero
model += [s != 0]
model += [m != 0]

# Equation: SEND + MORE = MONEY
# Convert each word to its numeric value
SEND = 1000 * s + 100 * e + 10 * n + d
MORE = 1000 * m + 100 * o + 10 * r + e
MONEY = 10000 * m + 1000 * o + 100 * n + 10 * e + y

# Add the equation constraint
model += [SEND + MORE == MONEY]

# Solve the model
model.solve()

# Print the solution in the correct order
solution = {
    "y": y.value(),
    "e": e.value(),
    "s": s.value(),
    "r": r.value(),
    "o": o.value(),
    "d": d.value(),
    "m": m.value(),
    "n": n.value()
}
print(json.dumps(solution))