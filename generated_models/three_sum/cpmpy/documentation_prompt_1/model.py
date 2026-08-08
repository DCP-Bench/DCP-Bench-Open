
import cpmpy as cp
import json

# Data
nums = [-1, 6, 8, 9, 10, -100, 78, 0, 1]

# Model definition
model = cp.Model()

n = len(nums)

# Decision Variables: selected[i] = 1 if nums[i] is selected, else 0
selected = cp.boolvar(shape=n, name="selected")

# Constraints
# Exactly three elements are selected
model += (cp.sum(selected) == 3)

# The sum of the selected elements is zero
model += (cp.sum([selected[i] * nums[i] for i in range(n)]) == 0)

# Solve and print
if model.solve():
    solution = {'indices': selected.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
