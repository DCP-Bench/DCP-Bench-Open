from cpmpy import *
import json

# Input data
nums = [-1, 6, 8, 9, 10, -100, 78, 0, 1]  # Collection of integers

# Parameters
n = len(nums)

# Decision variables
selected = boolvar(shape=n, name="selected")

# Model
model = Model()

# Exactly three elements must be selected
model += [sum(selected) == 3]

# The sum of the selected elements must be zero
model += [sum([nums[i] * selected[i] for i in range(n)]) == 0]

# Solve the model
model.solve()

# Print the solution
solution = {"indices": selected.value().tolist()}
print(json.dumps(solution))