
from ortools.sat.python import cp_model
import json

# Create the model
model = cp_model.CpModel()

# Decision Variables: each letter is a digit 0-9, with leading letters s and m non-zero
s = model.NewIntVar(1, 9, 's')
e = model.NewIntVar(0, 9, 'e')
n = model.NewIntVar(0, 9, 'n')
d = model.NewIntVar(0, 9, 'd')
m = model.NewIntVar(1, 9, 'm')
o = model.NewIntVar(0, 9, 'o')
r = model.NewIntVar(0, 9, 'r')
y = model.NewIntVar(0, 9, 'y')

# All letters must take different values
model.AddAllDifferent([s, e, n, d, m, o, r, y])

# Constraint: SEND + MORE = MONEY
# SEND = 1000*s + 100*e + 10*n + d
# MORE = 1000*m + 100*o + 10*r + e
# MONEY = 10000*m + 1000*o + 100*n + 10*e + y
model.Add(
    (1000 * s + 100 * e + 10 * n + d) +
    (1000 * m + 100 * o + 10 * r + e) ==
    (10000 * m + 1000 * o + 100 * n + 10 * e + y)
)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        's': solver.Value(s),
        'e': solver.Value(e),
        'n': solver.Value(n),
        'd': solver.Value(d),
        'm': solver.Value(m),
        'o': solver.Value(o),
        'r': solver.Value(r),
        'y': solver.Value(y)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
