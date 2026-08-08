
from ortools.sat.python import cp_model
import json

# Input data
nums = [-1, 6, 8, 9, 10, -100, 78, 0, 1]  # Collection of integers
n = len(nums)

# Model definition
model = cp_model.CpModel()

# Decision Variables: select[i] is 1 if nums[i] is selected, 0 otherwise
select = [model.NewBoolVar(f"select[{i}]") for i in range(n)]

# Constraints
# Exactly three elements must be selected
model.Add(sum(select) == 3)
# The sum of the selected elements must be zero
model.Add(sum(select[i] * nums[i] for i in range(n)) == 0)

# No objective (we just need any feasible solution), but OR-Tools requires one:
model.Minimize(0)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # Print a list indicating whether each element is selected (1) or not (0)
    solution = {
        'indices': [solver.Value(select[i]) for i in range(n)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
