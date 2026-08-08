
from ortools.sat.python import cp_model
import json

# Input data
base = 6  # Side length of the large square
sides = [3, 3, 3, 2, 1, 1, 1, 1, 1]  # Side lengths of the smaller squares

# Model definition
model = cp_model.CpModel()

# Decision Variables: x and y coordinates for each square's bottom-left corner
n = len(sides)
x = [model.NewIntVar(0, base - sides[i], f"x[{i}]") for i in range(n)]
y = [model.NewIntVar(0, base - sides[i], f"y[{i}]") for i in range(n)]

# Non-overlap constraints using disjunctive constraints
for i in range(n):
    for j in range(i + 1, n):
        # Boolean indicators for relative placement
        b0 = model.NewBoolVar(f"b0_{i}_{j}")  # i to the left of j
        b1 = model.NewBoolVar(f"b1_{i}_{j}")  # j to the left of i
        b2 = model.NewBoolVar(f"b2_{i}_{j}")  # i below j
        b3 = model.NewBoolVar(f"b3_{i}_{j}")  # j below i

        # If b0 then x[i] + sides[i] <= x[j]
        model.Add(x[i] + sides[i] <= x[j]).OnlyEnforceIf(b0)
        # If b1 then x[j] + sides[j] <= x[i]
        model.Add(x[j] + sides[j] <= x[i]).OnlyEnforceIf(b1)
        # If b2 then y[i] + sides[i] <= y[j]
        model.Add(y[i] + sides[i] <= y[j]).OnlyEnforceIf(b2)
        # If b3 then y[j] + sides[j] <= y[i]
        model.Add(y[j] + sides[j] <= y[i]).OnlyEnforceIf(b3)

        # At least one of the placement relations must hold
        model.AddBoolOr([b0, b1, b2, b3])

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x_coords': [solver.Value(x[i]) for i in range(n)],
        'y_coords': [solver.Value(y[i]) for i in range(n)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
