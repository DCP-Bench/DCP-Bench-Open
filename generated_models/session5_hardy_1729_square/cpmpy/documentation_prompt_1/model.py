
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: four different numbers between 1 and 100
a = cp.intvar(1, 100, name="a")
b = cp.intvar(1, 100, name="b")
c = cp.intvar(1, 100, name="c")
d = cp.intvar(1, 100, name="d")

# Constraints
model += (a != b)
model += (a != c)
model += (a != d)
model += (b != c)
model += (b != d)
model += (c != d)

# Sum of squares equality
model += (a*a + b*b == c*c + d*d)

# Solve and print
if model.solve():
    solution = {'a': int(a.value()), 'b': int(b.value()), 'c': int(c.value()), 'd': int(d.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
