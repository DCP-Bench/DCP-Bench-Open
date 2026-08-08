
from ortools.sat.python import cp_model
import json

# Create the model
model = cp_model.CpModel()

# Decision Variables: costs of each person in dollars
paper_hanger = model.NewIntVar(0, 10000, 'paper_hanger')
painter = model.NewIntVar(0, 10000, 'painter')
plumber = model.NewIntVar(0, 10000, 'plumber')
electrician = model.NewIntVar(0, 10000, 'electrician')
carpenter = model.NewIntVar(0, 10000, 'carpenter')
mason = model.NewIntVar(0, 10000, 'mason')

# Constraints based on pairwise payments
model.Add(paper_hanger + painter == 1100)
model.Add(painter + plumber == 1700)
model.Add(plumber + electrician == 1100)
model.Add(electrician + carpenter == 3300)
model.Add(carpenter + mason == 5300)
model.Add(mason + painter == 3200)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution as JSON
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'paper_hanger': solver.Value(paper_hanger),
        'painter': solver.Value(painter),
        'plumber': solver.Value(plumber),
        'electrician': solver.Value(electrician),
        'carpenter': solver.Value(carpenter),
        'mason': solver.Value(mason)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
