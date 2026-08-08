from ortools.sat.python import cp_model
import json

# Input data
n = 8  # Size of the Costas array

# Model definition
model = cp_model.CpModel()

# Decision Variables
# X: permutation of [0..n-1], representing the column positions of marks in each row
X = [model.NewIntVar(0, n - 1, f'X[{i}]') for i in range(n)]

# Add permutation constraint: all different
model.AddAllDifferent(X)

# Difference triangle variables and constraints
# For each lag l in 1..n-1, define differences D_l[i] = X[i] - X[i+l]
# Each line of the difference triangle must have all different values
for l in range(1, n):
    diff_vars = []
    for i in range(n - l):
        diff = model.NewIntVar(-(n - 1), n - 1, f'Diff_l{l}_i{i}')
        model.Add(diff == X[i] - X[i + l])
        diff_vars.append(diff)
    model.AddAllDifferent(diff_vars)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    costas = [solver.Value(x) for x in X]
    solution = {'costas': costas}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")