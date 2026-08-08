
import cpmpy as cp
import json

# Data
squares = [i*i for i in range(1, 101)]  # squares[0] = 1^2, ..., squares[99] = 100^2
# End of data

# Model definition
model = cp.Model()

# Decision Variables
a = cp.intvar(1, 100, name="a")
b = cp.intvar(1, 100, name="b")
c = cp.intvar(1, 100, name="c")
d = cp.intvar(1, 100, name="d")

sa = cp.intvar(1, 10000, name="sa")
sb = cp.intvar(1, 10000, name="sb")
sc = cp.intvar(1, 10000, name="sc")
sd = cp.intvar(1, 10000, name="sd")

# Constraints
# map variables to their squares using Element (zero-based index)
model += (sa == cp.Element(squares, a - 1))
model += (sb == cp.Element(squares, b - 1))
model += (sc == cp.Element(squares, c - 1))
model += (sd == cp.Element(squares, d - 1))

# equality of sums of squares
model += (sa + sb == sc + sd)

# all four numbers must be distinct
model += cp.AllDifferent(a, b, c, d)

# symmetry breaking: order each pair and order pairs lexicographically
model += (a < b)
model += (c < d)
model += cp.LexLess([a, b], [c, d])

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
