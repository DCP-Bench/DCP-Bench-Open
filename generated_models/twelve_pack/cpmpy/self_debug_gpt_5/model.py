
import cpmpy as cp
import json

# Data (optional)
target = 94  # Target number of beers
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# Upper bounds based on ceilings to ensure feasibility while keeping domains small
ub7 = (target + 7 - 1) // 7
ub13 = (target + 13 - 1) // 13
x7 = cp.intvar(0, ub7, name="x7")     # number of 7-packs
x13 = cp.intvar(0, ub13, name="x13")  # number of 13-packs

# Constraints
total_beers = 7 * x7 + 13 * x13
model += (total_beers >= target)

# Objective: minimize total beers (closest meeting or exceeding the target)
model.minimize(total_beers)

# Solve and print
if model.solve():
    solution = {'counts': [int(x7.value()), int(x13.value())]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
