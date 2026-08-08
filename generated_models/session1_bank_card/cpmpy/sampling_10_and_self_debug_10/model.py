
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: digits a, b, c, d (0-9)
a = cp.intvar(0, 9, name="a")
b = cp.intvar(0, 9, name="b")
c = cp.intvar(0, 9, name="c")
d = cp.intvar(0, 9, name="d")

# Constraints
# No two digits are the same
model += cp.AllDifferent([a, b, c, d])

# The 2-digit number cd is 3 times the 2-digit number ab
# cd = 10*c + d, ab = 10*a + b
model += (10*c + d) == 3 * (10*a + b)

# The 2-digit number da is 2 times the 2-digit number bc
# da = 10*d + a, bc = 10*b + c
model += (10*d + a) == 2 * (10*b + c)

# Solve and print
if model.solve():
    solution = {'a': int(a.value()), 'b': int(b.value()), 'c': int(c.value()), 'd': int(d.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
