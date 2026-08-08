
import cpmpy as cp
import json

# Variables
a = cp.intvar(1, 100, name="a")
b = cp.intvar(1, 100, name="b")
c = cp.intvar(1, 100, name="c")
d = cp.intvar(1, 100, name="d")

model = cp.Model()

# Constraints
model += cp.AllDifferent([a, b, c, d])
model += (a*a + b*b == c*c + d*d)

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
