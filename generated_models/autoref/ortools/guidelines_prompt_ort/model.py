
from ortools.sat.python import cp_model
import json

# Input data
n = 27
m = 5

# Model definition
model = cp_model.CpModel()

# Decision Variables: s[0] through s[n+1]
# Each s[i] is the number of occurrences of i in the series
s = [model.NewIntVar(0, n+1, f"s{i}") for i in range(n+2)]

# sn+1 must equal m
model.Add(s[n+1] == m)

# For counting occurrences, create boolean indicator eq[i][j] which is 1 if s[j] == i
eq = {}
for i in range(n+1):  # for each value i from 0 to n
    for j in range(n+2):  # for each position j in the series
        eq[(i, j)] = model.NewBoolVar(f"eq_{i}_{j}")
        # If eq[i,j] is true then s[j] == i
        model.Add(s[j] == i).OnlyEnforceIf(eq[(i, j)])
        # If eq[i,j] is false then s[j] != i
        model.Add(s[j] != i).OnlyEnforceIf(eq[(i, j)].Not())

# Constraint: for each i in 0..n, the number of positions j where s[j] == i equals s[i]
for i in range(n+1):
    model.Add(sum(eq[(i, j)] for j in range(n+2)) == s[i])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        's': [solver.Value(s[i]) for i in range(n+2)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
