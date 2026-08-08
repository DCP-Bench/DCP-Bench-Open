# Import libraries
from cpmpy import *
import json

# Parameters
nums = [-1, 6, 8, 9, 10, -100, 78, 0, 1]  # Collection of integers
n = len(nums)

# Decision Variables
indices = boolvar(shape=n, name="indices")  # Whether each element is selected

# Model
model = Model()

# Exactly three elements must be selected
model += sum(indices) == 3

# The sum of selected elements must be zero
model += sum([nums[i] * indices[i] for i in range(n)]) == 0

# Solve
model.solve()

# Print solution
solution = {
    "indices": [bool(idx) for idx in indices.value()]
}
print(json.dumps(solution))
# End of CPMPy script