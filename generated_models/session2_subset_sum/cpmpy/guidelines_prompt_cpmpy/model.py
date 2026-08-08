
import cpmpy as cp
import json

# Data
sizes = [16, 17, 23, 24, 39, 40]
# End of data

# Model definition
model = cp.Model()

# Decision Variables: number of stolen bags of each size
bags = cp.intvar(0, 6, shape=len(sizes), name="bags")

# Constraints
# Total stolen coins must sum to 100
model += cp.sum([bags[i] * sizes[i] for i in range(len(sizes))]) == 100

# Solve and print
if model.solve():
    solution = {'bags': bags.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
