
import cpmpy as cp
import json

# Decision Variables
a, b, c, d, e, f = cp.boolvar(shape=6, name=['artie', 'bill', 'crackitt', 'dodgy', 'edgy', 'fingers'])

model = cp.Model()

# Constraints
model += (a + b + c + d + e + f) <= 2  # At most 2 guilty

# Bill's constraint: b ↔ ¬c
model += (b == ~c)

# Dodgy's constraints
model += (~d).implies(c.implies(b))     # If innocent, c→b
model += d.implies(c & ~b)              # If guilty, c ∧ ¬b

# Edgy's constraints
count = a + b + c + d + e + f
model += (~e).implies(count != 1)       # If innocent, count ≠1
model += e.implies(count == 1)          # If guilty, count =1

# Fingers' constraints
model += (~f).implies(a & d)            # If innocent, a ∧ d
model += f.implies(~(a & d))            # If guilty, ¬(a ∧ d)

# Solve and print
if model.solve():
    solution = {
        'artie': int(a.value()),
        'bill': int(b.value()),
        'crackitt': int(c.value()),
        'dodgy': int(d.value()),
        'edgy': int(e.value()),
        'fingers': int(f.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
