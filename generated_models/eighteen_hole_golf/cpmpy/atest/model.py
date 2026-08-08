from cpmpy import *
import json

# Decision variables
# holes[i] is the length of the i-th hole, which can be 3, 4, or 5
holes = intvar(3, 5, shape=18, name="holes")

# Model
model = Model()

# Total length of the course is 72
model += [sum(holes) == 72]

# Solve the model
model.solve()

# Print the solution
solution = {"holes": holes.value().tolist()}
print(json.dumps(solution))