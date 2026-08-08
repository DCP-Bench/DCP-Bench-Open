
import cpmpy as cp
import json

# Data
target = 94  # Target number of beers
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# number of 7-packs (x) and 13-packs (y)
# bounds chosen generously (0..target) which is safe for this problem size
x = cp.intvar(0, target, name="x")
y = cp.intvar(0, target, name="y")

# auxiliary variables for total beers and excess over target
total = cp.intvar(0, 7 * target + 13 * target, name="total")
excess = cp.intvar(0, 7 * target + 13 * target, name="excess")

# Constraints
model += (total == 7 * x + 13 * y)
model += (total >= target)
model += (excess == total - target)

# Objective: minimize excess (closest meeting or exceeding the target)
model.minimize(excess)

# Solve and print
if model.solve():
    solution = {'counts': [int(x.value()), int(y.value())]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
