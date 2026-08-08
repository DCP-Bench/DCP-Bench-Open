from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision Variables: four different numbers between 1 and 100
a = model.NewIntVar(1, 100, 'a')
b = model.NewIntVar(1, 100, 'b')
c = model.NewIntVar(1, 100, 'c')
d = model.NewIntVar(1, 100, 'd')

# Constraint: all numbers must be different
model.AddAllDifferent([a, b, c, d])

# Constraint: a^2 + b^2 = c^2 + d^2
# Since OR-tools does not support direct multiplication of variables,
# we create auxiliary variables for squares and add constraints accordingly.

a_sq = model.NewIntVar(1, 10000, 'a_sq')
b_sq = model.NewIntVar(1, 10000, 'b_sq')
c_sq = model.NewIntVar(1, 10000, 'c_sq')
d_sq = model.NewIntVar(1, 10000, 'd_sq')

# Add multiplication constraints for squares
model.AddMultiplicationEquality(a_sq, [a, a])
model.AddMultiplicationEquality(b_sq, [b, b])
model.AddMultiplicationEquality(c_sq, [c, c])
model.AddMultiplicationEquality(d_sq, [d, d])

# Sum of squares equality
model.Add(a_sq + b_sq == c_sq + d_sq)

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