
import cpmpy as cp
import json

# Data
nums = [-1, 6, 8, 9, 10, -100, 78, 0, 1]  # Collection of integers
n = len(nums)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
indices = cp.boolvar(shape=n, name="indices")  # 1 if the element is selected, 0 otherwise

# Constraints
# Exactly three elements selected
model += (cp.sum(indices) == 3)

# The selected elements sum to zero
model += (cp.sum([indices[i] * nums[i] for i in range(n)]) == 0)

# Solve and print
if model.solve():
    # Convert boolean values to 0/1 integers as required
    solution = {'indices': [int(v) for v in indices.value().tolist()]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
