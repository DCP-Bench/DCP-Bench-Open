
from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision Variables: number of stolen bags for each bag size
b16 = model.NewIntVar(0, 100, 'b16')
b17 = model.NewIntVar(0, 100, 'b17')
b23 = model.NewIntVar(0, 100, 'b23')
b24 = model.NewIntVar(0, 100, 'b24')
b39 = model.NewIntVar(0, 100, 'b39')
b40 = model.NewIntVar(0, 100, 'b40')

# Constraint: total coins stolen equals 100
model.Add(16 * b16 + 17 * b17 + 23 * b23 + 24 * b24 + 39 * b39 + 40 * b40 == 100)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'bags': [
            solver.Value(b16),
            solver.Value(b17),
            solver.Value(b23),
            solver.Value(b24),
            solver.Value(b39),
            solver.Value(b40)
        ]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
