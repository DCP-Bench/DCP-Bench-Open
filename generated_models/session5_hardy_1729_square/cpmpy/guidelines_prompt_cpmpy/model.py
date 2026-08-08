
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
a = cp.IntVar(1, 100, name="a")
b = cp.IntVar(1, 100, name="b")
c = cp.IntVar(1, 100, name="c")
d = cp.IntVar(1, 100, name="d")

# Constraints
# All four numbers must be different
model += cp.all_different([a, b, c, d])
# Sum of squares of the first two equals sum of squares of the last two
model += a*a + b*b == c*c + d*d

# Solve and print
if model.solve():
    solution = {
        "a": int(a.value()),
        "b": int(b.value()),
        "c": int(c.value()),
        "d": int(d.value())
    }
    print(json.dumps(solution))
else:
    print("No solution found.")
