from cpmpy import *
import json

# Decision variables
a = intvar(1, 100, name="a")
b = intvar(1, 100, name="b")
c = intvar(1, 100, name="c")
d = intvar(1, 100, name="d")

# Model
model = Model()

# All numbers are different
model += [AllDifferent([a, b, c, d])]

# The sum of the squares of the first two numbers is equal to the sum of the squares of the other two numbers
model += [a**2 + b**2 == c**2 + d**2]

# Solve the model
model.solve()

# Print the solution
solution = {"a": a.value(), "b": b.value(), "c": c.value(), "d": d.value()}
print(json.dumps(solution))