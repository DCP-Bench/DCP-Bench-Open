
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
a = cp.intvar(1, 100, name="a")
b = cp.intvar(1, 100, name="b")
c = cp.intvar(1, 100, name="c")
d = cp.intvar(1, 100, name="d")

# Auxiliary variables for squares (avoid non-linear var*var by using Element)
a2 = cp.intvar(1, 10000, name="a2")
b2 = cp.intvar(1, 10000, name="b2")
c2 = cp.intvar(1, 10000, name="c2")
d2 = cp.intvar(1, 10000, name="d2")

# Precompute squares array for Element constraint (index 0 unused)
squares = [i*i for i in range(101)]  # squares[0]=0, squares[1]=1, ..., squares[100]=10000

# Constraints
model += cp.AllDifferent(a, b, c, d)

# Link variables to their squares via Element constraints
model += (a2 == cp.Element(squares, a))
model += (b2 == cp.Element(squares, b))
model += (c2 == cp.Element(squares, c))
model += (d2 == cp.Element(squares, d))

# Sum of squares equality
model += (a2 + b2 == c2 + d2)

# Optional symmetry breaking to speed up search (not required by problem)
model += (a < b)
model += (c < d)
model += ((a < c) | ((a == c) & (b <= d)))

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
