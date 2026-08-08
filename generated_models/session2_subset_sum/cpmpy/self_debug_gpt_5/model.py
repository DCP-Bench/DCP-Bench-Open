
import cpmpy as cp
import json

# Data
bag_sizes = [16, 17, 23, 24, 39, 40]
total_lost = 100
n_types = len(bag_sizes)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# Maximum number of bags cannot exceed 6 because 7*16 > 100
bags = cp.intvar(0, 6, shape=n_types, name="bags")

# Constraints
model += (cp.sum([bags[i] * bag_sizes[i] for i in range(n_types)]) == total_lost)

# Objective (none)

# Solve and print
if model.solve():
    solution = {'bags': bags.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
