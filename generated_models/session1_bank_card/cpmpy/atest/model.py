from cpmpy import *
import json

# Decision variables
a = intvar(0, 9, name="a")
b = intvar(0, 9, name="b")
c = intvar(0, 9, name="c")
d = intvar(0, 9, name="d")

# Model
model = Model()

# All digits are different
model += [AllDifferent([a, b, c, d])]

# The 2-digit number cd is 3 times the 2-digit number ab
model += [c * 10 + d == 3 * (a * 10 + b)]

# The 2-digit number da is 2 times the 2-digit number bc
model += [d * 10 + a == 2 * (b * 10 + c)]

# Solve the model
model.solve()

# Print the solution
solution = {"a": a.value(), "b": b.value(), "c": c.value(), "d": d.value()}
print(json.dumps(solution))