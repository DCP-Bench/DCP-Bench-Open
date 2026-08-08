
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: ages of the three sons (A1 >= A2 >= A3)
A1 = cp.intvar(1, 36, name="A1")
A2 = cp.intvar(1, 36, name="A2")
A3 = cp.intvar(1, 36, name="A3")

# Another triple (B1,B2,B3) representing a different possibility with same product and same sum
B1 = cp.intvar(1, 36, name="B1")
B2 = cp.intvar(1, 36, name="B2")
B3 = cp.intvar(1, 36, name="B3")

# Constraints
# Ordered so A1 is oldest
model += (A1 >= A2, A2 >= A3)
model += (B1 >= B2, B2 >= B3)

# Product of ages is 36 for both triples (the mathematician knew the product)
model += (A1 * A2 * A3 == 36)
model += (B1 * B2 * B3 == 36)

# The sum equals the number of windows; the mathematician still needed more information,
# so the sum must be ambiguous: there exists another distinct triple with the same sum
model += (A1 + A2 + A3 == B1 + B2 + B3)

# Ensure the other triple is actually different
model += ((A1 != B1) | (A2 != B2) | (A3 != B3))

# After hearing "the oldest son has blue eyes" the mathematician deduced the ages,
# which implies there is a unique oldest son in the correct triple
model += (A1 > A2)

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
