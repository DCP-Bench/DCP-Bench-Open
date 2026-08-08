
import cpmpy as cp
import json

# Variables representing the ages of the three sons, ordered from oldest to youngest (A1 >= A2 >= A3)
A1 = cp.intvar(1, 36, name="A1")
A2 = cp.intvar(1, 36, name="A2")
A3 = cp.intvar(1, 36, name="A3")

model = cp.Model()

# Constraints
model += (A1 * A2 * A3 == 36)  # Product of ages is 36
model += (A1 + A2 + A3 == 13)  # Sum must be ambiguous (only 13 has two triplets)
model += (A1 >= A2)            # Order constraints
model += (A2 >= A3)
model += (A1 > A2)             # Ensure a unique oldest son (A1 is strictly greater than A2)

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
