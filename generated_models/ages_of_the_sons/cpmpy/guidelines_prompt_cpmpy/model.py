
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: A1 is the oldest, then A2, then A3
A1 = cp.intvar(1, 36, name="A1")
A2 = cp.intvar(1, 36, name="A2")
A3 = cp.intvar(1, 36, name="A3")

# Constraints
# 1) The product of their ages is 36
model += (A1 * A2 * A3 == 36)
# 2) The sum of their ages is ambiguous (must be 13, since 13 is the only sum repeating among factor triples of 36)
model += (A1 + A2 + A3 == 13)
# 3) There is a single oldest son (so A1 must be strictly greater than both A2 and A3)
model += (A1 > A2)
model += (A1 > A3)

# Solve and print
if model.solve():
    solution = {
        'A1': int(A1.value()),
        'A2': int(A2.value()),
        'A3': int(A3.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
