
import cpmpy as cp
import json

# Data
target = 20
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# Number of 7-packs and 13-packs
counts = cp.intvar(0, target, shape=2, name="counts")

# Constraints
# The total number of beers must be at least the target
model += counts[0]*7 + counts[1]*13 >= target

# Objective: minimize the excess beers above the target
excess = counts[0]*7 + counts[1]*13 - target
model.minimize(excess)

# Solve and print
if model.solve():
    solution = {'counts': counts.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
