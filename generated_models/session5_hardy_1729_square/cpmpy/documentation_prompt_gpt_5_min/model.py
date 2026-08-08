
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
a = cp.intvar(1, 100, name="a")
b = cp.intvar(1, 100, name="b")
c = cp.intvar(1, 100, name="c")
d = cp.intvar(1, 100, name="d")

# Constraints
# all numbers are different
model += cp.AllDifferent(a, b, c, d)

# sum of squares equality
model += (a * a + b * b == c * c + d * d)

# Symmetry breaking (optional) to reduce equivalent permutations
model += a < b
model += c < d
# enforce an ordering between the pairs to avoid swapped pair solutions
model += cp.lex_less([a, b], [c, d])  # requires the first pair to be lexicographically smaller

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
