
from ortools.sat.python import cp_model
import json

# Create the CP model
model = cp_model.CpModel()

# Decision Variables
# Number of small chess sets to produce
small_set = model.NewIntVar(0, 200, 'small_set')
# Number of large chess sets to produce
large_set = model.NewIntVar(0, 100, 'large_set')

# Constraints
# Lathe hours constraint: 3 hours per small, 2 hours per large, total ≤ 160
model.Add(3 * small_set + 2 * large_set <= 160)

# Boxwood supply constraint: 1 kg per small, 3 kg per large, total ≤ 200
model.Add(small_set + 3 * large_set <= 200)

# Objective: maximize profit = 5 per small + 20 per large
model.Maximize(5 * small_set + 20 * large_set)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'small_set': solver.Value(small_set),
        'large_set': solver.Value(large_set),
        'max_profit': solver.ObjectiveValue()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
