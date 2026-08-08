
import cpmpy as cp
import json

model = cp.Model()

# Variables with appropriate domains
a = cp.intvar(1, 9, name="a")  # a cannot be 0 as it's the first digit of a two-digit number
b = cp.intvar(0, 9, name="b")
c = cp.intvar(0, 9, name="c")
d = cp.intvar(0, 9, name="d")

# Constraints
model += (10 * c + d == 3 * (10 * a + b))  # cd = 3 * ab
model += (10 * d + a == 2 * (10 * b + c))  # da = 2 * bc
model += cp.AllDifferent([a, b, c, d])     # All digits must be unique

# Solve and print the solution
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
