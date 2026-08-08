
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: letters as digits 0-9
s = cp.intvar(1, 9, name="s")  # cannot be zero
e = cp.intvar(0, 9, name="e")
n = cp.intvar(0, 9, name="n")
d = cp.intvar(0, 9, name="d")
m = cp.intvar(1, 9, name="m")  # cannot be zero
o = cp.intvar(0, 9, name="o")
r = cp.intvar(0, 9, name="r")
y = cp.intvar(0, 9, name="y")

letters = [s, e, n, d, m, o, r, y]

# All letters must be different digits
model += cp.AllDifferent(letters)

# Construct the numbers SEND, MORE, MONEY
send = s*1000 + e*100 + n*10 + d
more = m*1000 + o*100 + r*10 + e
money = m*10000 + o*1000 + n*100 + e*10 + y

# Constraint: SEND + MORE = MONEY
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
