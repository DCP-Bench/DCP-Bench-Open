
from ortools.sat.python import cp_model
import json

# Create the model
model = cp_model.CpModel()

# Decision variables: each digit of the PIN, from 1 to 9 (because each is part of a 2-digit number)
a = model.NewIntVar(1, 9, 'a')
b = model.NewIntVar(1, 9, 'b')
c = model.NewIntVar(1, 9, 'c')
d = model.NewIntVar(1, 9, 'd')

# All digits must be different
model.AddAllDifferent([a, b, c, d])

# Define the 2-digit numbers
ab = model.NewIntVar(10, 99, 'ab')
bc = model.NewIntVar(10, 99, 'bc')
cd = model.NewIntVar(10, 99, 'cd')
da = model.NewIntVar(10, 99, 'da')

# Link digits to the 2-digit numbers
model.Add(ab == a * 10 + b)
model.Add(bc == b * 10 + c)
model.Add(cd == c * 10 + d)
model.Add(da == d * 10 + a)

# Constraints given by the problem
# cd is 3 times ab
model.Add(cd == 3 * ab)
# da is 2 times bc
model.Add(da == 2 * bc)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
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
