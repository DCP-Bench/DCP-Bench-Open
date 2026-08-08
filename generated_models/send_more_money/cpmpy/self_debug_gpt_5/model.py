
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
s = cp.intvar(0, 9, name="s")
e = cp.intvar(0, 9, name="e")
n = cp.intvar(0, 9, name="n")
d = cp.intvar(0, 9, name="d")
m = cp.intvar(0, 9, name="m")
o = cp.intvar(0, 9, name="o")
r = cp.intvar(0, 9, name="r")
y = cp.intvar(0, 9, name="y")

# Constraints
model += cp.AllDifferent([s, e, n, d, m, o, r, y])
model += (s > 0)
model += (m > 0)

# SEND + MORE = MONEY
send = 1000*s + 100*e + 10*n + d
more = 1000*m + 100*o + 10*r + e
money = 10000*m + 1000*o + 100*n + 10*e + y
model += (send + more == money)

# Solve and print
if model.solve():
    solution = {
        's': int(s.value()),
        'e': int(e.value()),
        'n': int(n.value()),
        'd': int(d.value()),
        'm': int(m.value()),
        'o': int(o.value()),
        'r': int(r.value()),
        'y': int(y.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
