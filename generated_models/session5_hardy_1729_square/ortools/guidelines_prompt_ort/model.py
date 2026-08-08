
from ortools.sat.python import cp_model
import json

# Create the model
model = cp_model.CpModel()

# Decision variables: four different numbers between 1 and 100
a = model.NewIntVar(1, 100, 'a')
b = model.NewIntVar(1, 100, 'b')
c = model.NewIntVar(1, 100, 'c')
d = model.NewIntVar(1, 100, 'd')

# Auxiliary variables for squares
a_sq = model.NewIntVar(1, 10000, 'a_sq')
b_sq = model.NewIntVar(1, 10000, 'b_sq')
c_sq = model.NewIntVar(1, 10000, 'c_sq')
d_sq = model.NewIntVar(1, 10000, 'd_sq')

# Define squares via multiplication equality
model.AddMultiplicationEquality(a_sq, [a, a])
model.AddMultiplicationEquality(b_sq, [b, b])
model.AddMultiplicationEquality(c_sq, [c, c])
model.AddMultiplicationEquality(d_sq, [d, d])

# Constraint: sum of squares of a and b equals sum of squares of c and d
model.Add(a_sq + b_sq == c_sq + d_sq)

# All four numbers must be different
model.AddAllDifferent([a, b, c, d])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
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
