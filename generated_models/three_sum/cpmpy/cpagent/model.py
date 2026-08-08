import cpmpy as cp
import json

# Problem: Find three elements that sum to zero
# Input data
nums = [-1, 6, 8, 9, 10, -100, 78, 0, 1]
n = len(nums)

# Decision variables: boolean array indicating which elements are selected
selected = cp.boolvar(shape=n, name="selected")

# Create the model
model = cp.Model()

# Constraints:
# 1. Exactly 3 elements must be selected
model += cp.sum(selected) == 3

# 2. The sum of selected elements must equal 0
model += cp.sum([nums[i] * selected[i] for i in range(n)]) == 0

# Solve the model (satisfaction problem)
if model.solve():
    # Extract solution and convert to boolean list
    solution_values = selected.value()
    indices_bool = [bool(val) for val in solution_values]
    
    # Create output in required JSON format
    solution = {
        "indices": indices_bool
    }
    
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))