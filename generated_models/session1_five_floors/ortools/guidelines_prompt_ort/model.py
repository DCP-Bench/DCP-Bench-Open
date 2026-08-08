
from ortools.sat.python import cp_model
import json

# Create the model
model = cp_model.CpModel()

# Decision variables: floors 1 through 5
B = model.NewIntVar(1, 5, 'B')  # Baker
C = model.NewIntVar(1, 5, 'C')  # Cooper
F = model.NewIntVar(1, 5, 'F')  # Fletcher
M = model.NewIntVar(1, 5, 'M')  # Miller
S = model.NewIntVar(1, 5, 'S')  # Smith

# All must live on different floors
model.AddAllDifferent([B, C, F, M, S])

# Constraints from the problem
model.Add(B != 5)         # Baker does not live on the fifth floor
model.Add(C != 1)         # Cooper does not live on the first floor
model.Add(F != 1)         # Fletcher does not live on the first floor
model.Add(F != 5)         # Fletcher does not live on the fifth floor
model.Add(M > C)          # Miller lives on a higher floor than Cooper
# Smith does not live adjacent to Fletcher
model.Add(S != F + 1)
model.Add(S != F - 1)
# Fletcher does not live adjacent to Cooper
model.Add(F != C + 1)
model.Add(F != C - 1)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
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
