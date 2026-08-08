
import cpmpy as cp
import json

# Precompute squares for indices 0..1000
squares = [i * i for i in range(1001)]

# Model definition
model = cp.Model()

# Decision Variables: allow indices 1..1000 (0 unused)
a = cp.intvar(1, 1000, name="a")
b = cp.intvar(1, 1000, name="b")
c = cp.intvar(1, 1000, name="c")

# Constraints
model += (a + b + c == 1000)                                   # sum constraint
model += (a < b)                                                # order to avoid symmetric solutions
model += (b < c)
# Use Element to map variable value to its square (avoids nonlinear var*var)
model += (cp.Element(squares, a) + cp.Element(squares, b) == cp.Element(squares, c))

# Solve and print
if model.solve():
    solution = {'a': int(a.value()), 'b': int(b.value()), 'c': int(c.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
