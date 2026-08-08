
from ortools.sat.python import cp_model
import json

# Create the CP model
model = cp_model.CpModel()

# Decision Variables: 18 holes with lengths 3, 4, or 5
holes = [model.NewIntVar(3, 5, f"hole_{i}") for i in range(18)]

# Constraint: total length of the course must be 72
model.Add(sum(holes) == 72)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'holes': [solver.Value(holes[i]) for i in range(18)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
