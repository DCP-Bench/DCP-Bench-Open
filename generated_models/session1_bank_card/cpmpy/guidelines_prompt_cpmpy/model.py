
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: PIN digits a, b, c, d (0..9)
a = cp.IntVar(0, 9, name="a")
b = cp.IntVar(0, 9, name="b")
c = cp.IntVar(0, 9, name="c")
d = cp.IntVar(0, 9, name="d")

# Constraints
# 1) All digits are different
model += cp.AllDifferent([a, b, c, d])

# 2) The 2-digit number cd = 3 * the 2-digit number ab
model += 10 * c + d == 3 * (10 * a + b)

# 3) The 2-digit number da = 2 * the 2-digit number bc
model += 10 * d + a == 2 * (10 * b + c)

# Solve and print
if model.solve():
    solution = {
        "a": int(a.value()),
        "b": int(b.value()),
        "c": int(c.value()),
        "d": int(d.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
