
import cpmpy as cp
import json

nums = [-1, 6, 8, 9, 10, -100, 78, 0, 1]

model = cp.Model()

# Decision variables: boolean array indicating if each element is selected
selected = cp.boolvar(shape=len(nums), name="selected")

# Constraints
model += (cp.sum(selected) == 3)  # Exactly three elements must be selected
sum_expression = cp.sum([nums[i] * selected[i] for i in range(len(nums))])
model += (sum_expression == 0)    # Their sum must be zero

# Solve
if model.solve():
    selected_values = selected.value().tolist()
    solution = {i: int(selected_values[i]) for i in range(len(nums))}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
