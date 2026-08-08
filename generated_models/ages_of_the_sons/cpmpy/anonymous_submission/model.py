# Import libraries
from cpmpy import *
import json

# Decision Variables
A1 = intvar(1, 36, name="A1")  # Oldest son's age
A2 = intvar(1, 36, name="A2")  # Middle son's age
A3 = intvar(1, 36, name="A3")  # Youngest son's age

# Model
model = Model()

# Constraint: product of ages is 36
model += (A1 * A2 * A3) == 36

# Constraint: ages are in strictly decreasing order (A1 > A2 >= A3)
model += (A1 > A2)
model += (A2 >= A3)

# Additional constraint: sum must be ambiguous (13 is the only sum that appears twice)
# We model this by ensuring the sum is 13 (since other sums would have been unique)
model += (A1 + A2 + A3) == 13

# Solve
model.solve()

# Print solution
solution = {
    "A1": A1.value(),
    "A2": A2.value(),
    "A3": A3.value()
}
print(json.dumps(solution))
# End of CPMPy script