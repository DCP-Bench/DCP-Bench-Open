from ortools.sat.python import cp_model
import json

# Input data
n = 5  # Length of x
m = 3  # Number of values
v = [1, 5, 8]  # Values to be among in x

# Model definition
model = cp_model.CpModel()

# Decision Variables: x[i] can be any integer, but to keep it simple, we limit domain to 0..10
# (assuming values outside v are allowed but not counted)
x = [model.NewIntVar(0, 10, f'x{i}') for i in range(n)]

# Create boolean variables indicating if x[i] is in v
in_v = []
for i in range(n):
    b = model.NewBoolVar(f'in_v_{i}')
    # b is true if x[i] is in v
    model.AddAllowedAssignments([x[i]], [(val,) for val in v]).OnlyEnforceIf(b)
    model.AddForbiddenAssignments([x[i]], [(val,) for val in v]).OnlyEnforceIf(b.Not())
    in_v.append(b)

# Constraint: Exactly m variables in x take one of the values in v
model.Add(sum(in_v) == m)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x': [solver.Value(var) for var in x]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")