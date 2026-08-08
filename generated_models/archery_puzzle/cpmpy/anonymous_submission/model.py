# Import libraries
from cpmpy import *
import json

# Parameters
targets = [16, 17, 23, 24, 39, 40]  # Available target values
max_arrows = 100  # Upper bound on number of arrows

# Decision Variables
hits = intvar(0, max_arrows, shape=len(targets), name="hits")  # Number of hits per target
total = intvar(0, 100*max_arrows, name="total")  # Total score

# Model
model = Model()

# Calculate total score
model += total == sum(hits[i] * targets[i] for i in range(len(targets)))

# Objective: minimize the absolute difference from 100
diff = intvar(0, 100*max_arrows, name="diff")
model += (diff == abs(total - 100))
model.minimize(diff)

# Solve
model.solve()

# Print solution
solution = {
    "hits": hits.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script