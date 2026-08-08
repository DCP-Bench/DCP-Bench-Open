
import cpmpy as cp
import json

# Data
nums = [-1, 6, 8, 9, 10, -100, 78, 0, 1]
n = len(nums)
# End of data

# Model definition
model = cp.Model()

# Decision Variables
# selected[i] = 1 if nums[i] is chosen, 0 otherwise
selected = cp.BoolVar(shape=n, name="selected")

# Constraints
# Exactly three elements are selected
model += (cp.sum(selected) == 3)
# The sum of the selected elements must be zero
model += (cp.sum([nums[i] * selected[i] for i in range(n)]) == 0)

# Solve and print
if model.solve():
    solution = {
        "selected": [int(v) for v in selected.value().tolist()]
    }
    print(json.dumps(solution))
else:
    print("No solution found.")
