
import cpmpy as cp
import json

# Data: denominations of coins per bag
denoms = [16, 17, 23, 24, 39, 40]

# Model definition
model = cp.Model()

# Decision Variables: number of stolen bags for each type (in same order as denoms)
bags = cp.intvar(0, 6, shape=6, name="bags")  # upper bound 6 is safe since 100//16 = 6

# Constraints: total coins lost equals 100
model += (cp.sum([denoms[i] * bags[i] for i in range(6)]) == 100)

# Solve and print
if model.solve():
    solution = {'bags': bags.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
