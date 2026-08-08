from cpmpy import *
import json

# Numbers on the dummies
dummies_numbers = [15, 9, 30, 21, 19, 3, 12, 6, 25, 27]

# Decision variables
# selected[i] = 1 if dummy i is knocked over, 0 otherwise
selected = boolvar(shape=len(dummies_numbers), name="dummies")

# Model
model = Model()

# The sum of the numbers on the knocked over dummies must be exactly 50
model += [sum([dummies_numbers[i] * selected[i] for i in range(len(dummies_numbers))]) == 50]

# Solve the model
model.solve()

# Print the solution
solution = {"dummies": selected.value().tolist()}
print(json.dumps(solution))