
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: digits of the PIN
a = cp.intvar(0, 9, name="a")
b = cp.intvar(0, 9, name="b")
c = cp.intvar(0, 9, name="c")
d = cp.intvar(0, 9, name="d")

# Constraints
model += cp.AllDifferent([a, b, c, d])
# Each is a leading digit of a two-digit number, so none can be zero
model += (a != 0)
model += (b != 0)
model += (c != 0)
model += (d != 0)

# Two-digit number constraints
model += (10*c + d == 3 * (10*a + b))  # cd = 3 * ab
model += (10*d + a == 2 * (10*b + c))  # da = 2 * bc

# Solve and print
if model.solve():
    solution = {
        'a': int(a.value()),
        'b': int(b.value()),
        'c': int(c.value()),
        'd': int(d.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
