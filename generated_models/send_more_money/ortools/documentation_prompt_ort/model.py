from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Letters as variables with domain 0-9
s = model.NewIntVar(1, 9, 's')  # S cannot be zero (leading digit)
e = model.NewIntVar(0, 9, 'e')
n = model.NewIntVar(0, 9, 'n')
d = model.NewIntVar(0, 9, 'd')
m = model.NewIntVar(1, 9, 'm')  # M cannot be zero (leading digit)
o = model.NewIntVar(0, 9, 'o')
r = model.NewIntVar(0, 9, 'r')
y = model.NewIntVar(0, 9, 'y')

letters = [s, e, n, d, m, o, r, y]

# All letters must be assigned unique digits
model.AddAllDifferent(letters)

# Construct the numbers SEND, MORE, MONEY
# SEND = 1000*S + 100*E + 10*N + D
send = s * 1000 + e * 100 + n * 10 + d
# MORE = 1000*M + 100*O + 10*R + E
more = m * 1000 + o * 100 + r * 10 + e
# MONEY = 10000*M + 1000*O + 100*N + 10*E + Y
money = m * 10000 + o * 1000 + n * 100 + e * 10 + y

# Constraint: SEND + MORE = MONEY
model.Add(send + more == money)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

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