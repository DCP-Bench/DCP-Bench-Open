from cpmpy import *
import json

# Decision Variables
# Number of bags stolen for each type (16, 17, 23, 24, 39, 40 coins)
bags = intvar(0, 100, shape=6, name="bags")

# Model
model = Model()

# Constraints
# Total coins stolen must be 100
model += (16*bags[0] + 17*bags[1] + 23*bags[2] + 24*bags[3] + 39*bags[4] + 40*bags[5] == 100)

# Solve
model.solve()

# Print solution
solution = {
    "bags": bags.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script