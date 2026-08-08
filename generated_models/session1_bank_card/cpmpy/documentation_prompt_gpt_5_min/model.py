
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: digits a, b, c, d (each is a non-zero digit since they form 2-digit numbers)
a = cp.intvar(1, 9, name="a")
b = cp.intvar(1, 9, name="b")
c = cp.intvar(1, 9, name="c")
d = cp.intvar(1, 9, name="d")

# Constraints
model += cp.AllDifferent(a, b, c, d)  # no two digits are the same

# cd = 3 * ab  -> 10*c + d = 3*(10*a + b)
model += (10*c + d == 3*(10*a + b))

# da = 2 * bc  -> 10*d + a = 2*(10*b + c)
model += (10*d + a == 2*(10*b + c))

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
