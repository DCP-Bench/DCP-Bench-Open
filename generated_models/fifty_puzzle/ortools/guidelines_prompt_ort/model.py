
from ortools.sat.python import cp_model
import json

# Input data: values on the ten dummies
values = [15, 9, 30, 21, 19, 3, 12, 6, 25, 27]

# Create the CP-SAT model
model = cp_model.CpModel()

# Decision variables: x[i] is 1 if dummy i is knocked over, 0 otherwise
x = [model.NewBoolVar(f'x[{i}]') for i in range(len(values))]

# Constraint: the sum of knocked-over dummy values must be exactly 50
model.Add(sum(x[i] * values[i] for i in range(len(values))) == 50)

# Solve the model (no objective; just find a feasible solution)
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the knocked-over dummies in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'dummies': [values[i] for i in range(len(values)) if solver.Value(x[i]) == 1]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
