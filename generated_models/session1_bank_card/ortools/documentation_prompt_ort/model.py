from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision Variables: digits a, b, c, d (0-9)
a = model.NewIntVar(0, 9, 'a')
b = model.NewIntVar(0, 9, 'b')
c = model.NewIntVar(0, 9, 'c')
d = model.NewIntVar(0, 9, 'd')

# Constraint: no two digits are the same
model.AddAllDifferent([a, b, c, d])

# Define two-digit numbers as expressions
ab = a * 10 + b
bc = b * 10 + c
cd = c * 10 + d
da = d * 10 + a

# Constraint: cd = 3 * ab
model.Add(cd == 3 * ab)

# Constraint: da = 2 * bc
model.Add(da == 2 * bc)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'a': solver.Value(a),
        'b': solver.Value(b),
        'c': solver.Value(c),
        'd': solver.Value(d)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")