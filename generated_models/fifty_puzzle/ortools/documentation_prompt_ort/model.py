from ortools.sat.python import cp_model
import json

# Numbers on the ten dummies
numbers = [15, 9, 30, 21, 19, 3, 12, 6, 25, 27]

# Model definition
model = cp_model.CpModel()

# Decision variables: whether each dummy is knocked over (1) or not (0)
dummies = [model.NewBoolVar(f'dummy_{i}') for i in range(len(numbers))]

# Constraint: sum of numbers on knocked down dummies must be exactly 50
model.Add(sum(dummies[i] * numbers[i] for i in range(len(numbers))) == 50)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'dummies': [solver.Value(d) for d in dummies]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")