# Import libraries
from cpmpy import *
import json

# Parameters
target = 20  # Target number of beers
max_packs = 100  # Upper bound on number of packs

# Decision Variables
counts = intvar(0, max_packs, shape=2, name="counts")  # [7-packs, 13-packs]
total = intvar(0, max_packs*(7+13), name="total")  # Total number of beers

# Model
model = Model()

# Calculate total number of beers
model += total == 7*counts[0] + 13*counts[1]

# Constraint: total must meet or exceed target
model += total >= target

# Objective: minimize the difference from target (since we already meet it)
diff = intvar(0, max_packs*(7+13), name="diff")
model += (diff == total - target)
model.minimize(diff)

# Solve
model.solve()

# Print solution
solution = {
    "counts": counts.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script