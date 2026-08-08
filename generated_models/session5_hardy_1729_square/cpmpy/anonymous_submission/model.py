# Import libraries
from cpmpy import *
import json

# Decision Variables
a = intvar(1, 100, name="a")  # First number
b = intvar(1, 100, name="b")  # Second number
c = intvar(1, 100, name="c")  # Third number
d = intvar(1, 100, name="d")  # Fourth number

# Model
model = Model()

# Constraint: All numbers must be distinct
model += AllDifferent([a, b, c, d])

# Constraint: a^2 + b^2 = c^2 + d^2
model += (a**2 + b**2) == (c**2 + d**2)

# Solve
model.solve()

# Print solution
solution = {
    "a": a.value(),
    "b": b.value(),
    "c": c.value(),
    "d": d.value()
}
print(json.dumps(solution))
# End of CPMPy script