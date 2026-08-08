from cpmpy import *
import json

# Input data
target = 20  # Target number of beers

# Decision variables
# counts[0] is the number of 7-packs
# counts[1] is the number of 13-packs
counts = intvar(0, 100, shape=2, name="counts")

# Model
model = Model()

# Total number of beers must be at least the target
model += [7 * counts[0] + 13 * counts[1] >= target]

# Objective: minimize the excess over the target
model.minimize(7 * counts[0] + 13 * counts[1] - target)

# Solve the model
model.solve()

# Print the solution
solution = {"counts": counts.value().tolist()}
print(json.dumps(solution))