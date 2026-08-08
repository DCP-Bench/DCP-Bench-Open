
from ortools.sat.python import cp_model
import json

# Input data
target = 20  # Target number of beers

# Model definition
model = cp_model.CpModel()

# Decision Variables: number of 7-packs (x) and 13-packs (y)
# We bound them between 0 and target since more packs than target is unnecessary
x = model.NewIntVar(0, target, 'x')
y = model.NewIntVar(0, target, 'y')

# Constraint: total beers must meet or exceed the target
model.Add(7 * x + 13 * y >= target)

# Objective: minimize the total number of beers (to get the closest combination)
model.Minimize(7 * x + 13 * y)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'counts': [solver.Value(x), solver.Value(y)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
