
import cpmpy as cp
import json

# Data (optional)
nums = [-1, 6, 8, 9, 10, -100, 78, 0, 1]  # Collection of integers
# End of data

# Model definition
model = cp.Model()

# Decision Variables
n = len(nums)
indices = cp.boolvar(shape=n, name="indices")

# Constraints
# Select exactly three elements
model += (cp.sum(indices) == 3)
# The sum of the selected elements equals zero
model += (cp.sum([indices[i] * nums[i] for i in range(n)]) == 0)

# Objective (optional)
# No objective needed; just find any feasible solution

# Solve and print
if model.solve():
    solution = {'indices': [int(v) for v in indices.value().tolist()]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
