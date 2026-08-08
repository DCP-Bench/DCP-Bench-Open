
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: four different numbers between 1 and 100
a = cp.intvar(1, 100, name="a")
b = cp.intvar(1, 100, name="b")
c = cp.intvar(1, 100, name="c")
d = cp.intvar(1, 100, name="d")

# All four numbers must be different
model += cp.AllDifferent([a, b, c, d])

# Constraint: sum of squares of first two equals sum of squares of last two
model += (a * a + b * b == c * c + d * d)

# Solve and print
if model.solve():
    solution = {'a': int(a.value()), 'b': int(b.value()), 'c': int(c.value()), 'd': int(d.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
