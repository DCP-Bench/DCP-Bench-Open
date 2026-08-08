from ortools.sat.python import cp_model
import json

# Input data
nums = [-1, 6, 8, 9, 10, -100, 78, 0, 1]

# Model definition
model = cp_model.CpModel()

n = len(nums)

# Decision variables: selected[i] = 1 if nums[i] is selected, 0 otherwise
selected = [model.NewBoolVar(f'selected_{i}') for i in range(n)]

# Constraint: Exactly three elements are selected
model.Add(sum(selected) == 3)

# Constraint: The sum of the selected elements is zero
# We use a linear expression sum(nums[i] * selected[i]) == 0
model.Add(sum(nums[i] * selected[i] for i in range(n)) == 0)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'selected': [solver.Value(var) for var in selected]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")