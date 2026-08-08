
from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision Variables
men = model.NewIntVar(0, 100, 'men')
women = model.NewIntVar(0, 100, 'women')
children = model.NewIntVar(0, 100, 'children')

# Constraints
# 1) Total people is 100
model.Add(men + women + children == 100)
# 2) Total bushels: 3 per man, 2 per woman, 0.5 per child -> multiply by 2 to keep integers
model.Add(6 * men + 4 * women + children == 200)
# 3) There are five times as many women as men
model.Add(women == 5 * men)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'men': solver.Value(men),
        'women': solver.Value(women),
        'children': solver.Value(children)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
