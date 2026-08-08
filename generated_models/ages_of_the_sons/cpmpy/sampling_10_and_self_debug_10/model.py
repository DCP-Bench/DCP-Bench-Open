
import cpmpy as cp
import json

# Variables for the first triple (the sons' ages)
A = cp.intvar(1, 36, shape=3, name="A")
A1, A2, A3 = A

# Variables for the second triple (to check ambiguous sum)
B = cp.intvar(1, 36, shape=3, name="B")
B1, B2, B3 = B

model = cp.Model()

# Ordering constraints (descending)
model += (A1 >= A2)
model += (A2 >= A3)

model += (B1 >= B2)
model += (B2 >= B3)

# Product constraints
model += (A1 * A2 * A3 == 36)
model += (B1 * B2 * B3 == 36)

# Sum equality (ambiguous sum)
model += (A1 + A2 + A3 == B1 + B2 + B3)

# The two triples must be different
model += ((A1 != B1) | (A2 != B2) | (A3 != B3))

# Unique oldest son
model += (A1 > A2)

# Solve the model
if model.solve():
    solution = {
        'A1': int(A1.value()),
        'A2': int(A2.value()),
        'A3': int(A3.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
