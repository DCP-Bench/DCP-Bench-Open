# Import libraries
from cpmpy import *
import json

# Decision Variables
a = intvar(0, 9, name="a")  # First digit
b = intvar(0, 9, name="b")  # Second digit
c = intvar(0, 9, name="c")  # Third digit
d = intvar(0, 9, name="d")  # Fourth digit

# Model
model = Model()

# Constraint: All digits must be distinct
model += AllDifferent([a, b, c, d])

# Constraint: cd is 3 times ab
ab = 10*a + b
cd = 10*c + d
model += cd == 3 * ab

# Constraint: da is 2 times bc
bc = 10*b + c
da = 10*d + a
model += da == 2 * bc

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