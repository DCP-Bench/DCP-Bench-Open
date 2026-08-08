# Import libraries
from cpmpy import *
import json

# Parameters
n = 8  # Size of the Costas array

# Decision Variables
costas = intvar(1, n, shape=n, name="costas")  # Costas array

# Model
model = Model()

# Constraint: costas is a permutation (all different)
model += AllDifferent(costas)

# Constraints for difference triangle
for l in range(1, n):
    # Create difference variables for this length
    diffs = intvar(-n+1, n-1, shape=(n-l,), name=f"diffs_l{l}")
    for i in range(n-l):
        model += (diffs[i] == costas[i] - costas[i+l])  # Corrected subtraction order
    # Each line in difference triangle must be all different
    model += AllDifferent(diffs)

# Solve
model.solve()

# Print solution
solution = {"costas": costas.value().tolist()}
print(json.dumps(solution))
# End of CPMPy script