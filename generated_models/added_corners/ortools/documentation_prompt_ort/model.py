from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Positions:
# Circles: C1, C2, C3, C4 (corners)
# Squares: F1, F2, F3, F4 (edges)
# Layout:
#   C1 F1 C2
#   F4    F2
#   C4 F3 C3

# Decision Variables: digits 1 through 8, all different
digits = range(1, 9)
C = [model.NewIntVar(1, 8, f'C{i+1}') for i in range(4)]
F = [model.NewIntVar(1, 8, f'F{i+1}') for i in range(4)]

# All digits must be different
model.AddAllDifferent(C + F)

# Constraints: each square equals sum of adjoining circles
# F1 = C1 + C2
model.Add(F[0] == C[0] + C[1])
# F2 = C2 + C3
model.Add(F[1] == C[1] + C[2])
# F3 = C3 + C4
model.Add(F[2] == C[2] + C[3])
# F4 = C4 + C1
model.Add(F[3] == C[3] + C[0])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    positions = {
        'C1': solver.Value(C[0]),
        'F1': solver.Value(F[0]),
        'C2': solver.Value(C[1]),
        'F2': solver.Value(F[1]),
        'C3': solver.Value(C[2]),
        'F3': solver.Value(F[2]),
        'C4': solver.Value(C[3]),
        'F4': solver.Value(F[3])
    }
    print(json.dumps({'positions': positions}, indent=4))
else:
    print("No solution found.")