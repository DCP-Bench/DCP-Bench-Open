
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
s, e, n, d, m, o, r, y = letters = cp.intvar(0, 9, shape=8, name="letters")

# Constraints
model += cp.AllDifferent(letters)      # all letters different
model += s != 0                        # leading letter of SEND cannot be zero
model += m != 0                        # leading letter of MORE/MONEY cannot be zero

# Numeric formation of the words
send  = 1000*s + 100*e + 10*n + d
more  = 1000*m + 100*o + 10*r + e
money = 10000*m + 1000*o + 100*n + 10*e + y

# Cryptarithmetic equation
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
