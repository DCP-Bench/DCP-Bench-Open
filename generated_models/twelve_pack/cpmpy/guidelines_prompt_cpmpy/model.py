
import cpmpy as cp
import json

# Data
target = 20
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# Upper bounds are set to just above the number of packs needed if using only that pack type
max7 = (target + 6) // 7 + 1   # ceil(target/7) + 1
max13 = (target + 12) // 13 + 1  # ceil(target/13) + 1
x7 = cp.IntVar(0, max7, name="x7")     # number of 7-packs
x13 = cp.IntVar(0, max13, name="x13")  # number of 13-packs

# Constraints
model += 7 * x7 + 13 * x13 >= target

# Objective: minimize the total number of beers (to be as close as possible to target from above)
model.minimize(7 * x7 + 13 * x13)

# Solve and print
if model.solve():
    solution = {
        "counts": [int(x7.value()), int(x13.value())]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
