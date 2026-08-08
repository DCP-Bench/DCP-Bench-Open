from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision Variables: 18 holes, each length in {3,4,5}
holes = [model.NewIntVar(3, 5, f'hole_{i}') for i in range(18)]

# Constraint: total length of the course is 72
model.Add(sum(holes) == 72)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'holes': [solver.Value(h) for h in holes]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")