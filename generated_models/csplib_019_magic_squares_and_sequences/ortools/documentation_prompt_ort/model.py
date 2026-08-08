from ortools.sat.python import cp_model
import json

# Input data
n = 12  # Length of the magic sequence

# Model definition
model = cp_model.CpModel()

# Decision Variables
# x[i] is the number of times i occurs in the sequence
x = [model.NewIntVar(0, n - 1, f'x[{i}]') for i in range(n)]

# Constraints
# The sum of all x[i] must be n (the length of the sequence)
model.Add(sum(x) == n)

# For each i, x[i] must be equal to the count of i in the sequence
# Since x[i] is the count of i, sum of indicators (x[j] == i) over j must be x[i]
# We model this by counting how many x[j] equal i for j in 0..n-1
# We use boolean variables to represent (x[j] == i)
for i in range(n):
    bool_vars = []
    for j in range(n):
        b = model.NewBoolVar(f'is_{i}_at_{j}')
        model.Add(x[j] == i).OnlyEnforceIf(b)
        model.Add(x[j] != i).OnlyEnforceIf(b.Not())
        bool_vars.append(b)
    model.Add(x[i] == sum(bool_vars))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {'x': [solver.Value(var) for var in x]}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")