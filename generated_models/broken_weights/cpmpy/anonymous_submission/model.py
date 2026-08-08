# Import libraries
from cpmpy import *
import json

# Decision Variables
weights = intvar(1, 40, shape=4, name="weights")  # Weights of the four pieces

# Model
model = Model()

# Constraint: sum of weights is 40 pounds
model += sum(weights) == 40

# Constraint: all weights are distinct
model += AllDifferent(weights)

# Constraint: can measure every weight from 1 to 40
# We model this by ensuring for each target weight (1..40),
# there exists a subset of weights that can balance it (considering both sides of the scale)
for target in range(1, 41):
    # Create auxiliary variables for each weight indicating if it's:
    # 0: not used, 1: on left side, 2: on right side
    aux_vars = intvar(0, 2, shape=4, name=f"aux_{target}")
    
    # The difference between left and right sides should equal the target
    left = sum(weights[i] * (aux_vars[i] == 1) for i in range(4))
    right = sum(weights[i] * (aux_vars[i] == 2) for i in range(4))
    model += (left - right == target) | (right - left == target)

# Solve
model.solve()

# Print solution
solution = {
    "weights": sorted(weights.value().tolist())  # Sorting for readability
}
print(json.dumps(solution))
# End of CPMPy script