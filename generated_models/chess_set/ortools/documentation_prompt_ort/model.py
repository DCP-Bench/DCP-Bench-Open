from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision Variables
# Number of small sets produced (non-negative integer)
small_set = model.NewIntVar(0, 1000, 'small_set')
# Number of large sets produced (non-negative integer)
large_set = model.NewIntVar(0, 1000, 'large_set')

# Constraints
# Lathe hours constraint: 3 hours per small set + 2 hours per large set <= 160 hours
model.Add(3 * small_set + 2 * large_set <= 160)

# Boxwood constraint: 1 kg per small set + 3 kg per large set <= 200 kg
model.Add(small_set + 3 * large_set <= 200)

# Objective function: maximize profit = 5 * small_set + 20 * large_set
model.Maximize(5 * small_set + 20 * large_set)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'small_set': solver.Value(small_set),
        'large_set': solver.Value(large_set),
        'max_profit': solver.ObjectiveValue()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")