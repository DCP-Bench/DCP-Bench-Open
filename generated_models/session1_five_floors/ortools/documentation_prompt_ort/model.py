from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision Variables: floors for each person (1 to 5)
B = model.NewIntVar(1, 5, 'B')  # Baker
C = model.NewIntVar(1, 5, 'C')  # Cooper
F = model.NewIntVar(1, 5, 'F')  # Fletcher
M = model.NewIntVar(1, 5, 'M')  # Miller
S = model.NewIntVar(1, 5, 'S')  # Smith

# All live on different floors
model.AddAllDifferent([B, C, F, M, S])

# Constraints from the problem
model.Add(B != 5)  # Baker does not live on the fifth floor
model.Add(C != 1)  # Cooper does not live on the first floor
model.Add(F != 1)  # Fletcher does not live on the first floor
model.Add(F != 5)  # Fletcher does not live on the fifth floor
model.Add(M > C)   # Miller lives on a higher floor than Cooper

# Smith does not live on a floor adjacent to Fletcher's
model.AddAbsEquality(model.NewIntVar(1, 4, 'abs_SF'), S - F)
model.Add(S - F != 1)
model.Add(F - S != 1)

# Fletcher does not live on a floor adjacent to Cooper's
model.AddAbsEquality(model.NewIntVar(1, 4, 'abs_FC'), F - C)
model.Add(F - C != 1)
model.Add(C - F != 1)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'B': solver.Value(B),
        'C': solver.Value(C),
        'F': solver.Value(F),
        'M': solver.Value(M),
        'S': solver.Value(S)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")