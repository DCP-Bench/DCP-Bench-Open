from ortools.sat.python import cp_model
import json

# Input data
base = 6  # Side length of the large square
sides = [3, 3, 3, 2, 1, 1, 1, 1, 1]  # Side lengths of the smaller squares
n = len(sides)

# Model definition
model = cp_model.CpModel()

# Decision Variables: x and y coordinates of the bottom-left corner of each square
x_coords = [model.NewIntVar(0, base - sides[i], f'x_{i}') for i in range(n)]
y_coords = [model.NewIntVar(0, base - sides[i], f'y_{i}') for i in range(n)]

# Constraints

# 1. Squares must be inside the big square (already ensured by variable domains)

# 2. No overlap between any two squares
for i in range(n):
    for j in range(i + 1, n):
        # At least one of these must be true to avoid overlap:
        # square i is to the left of square j
        no_overlap_x = model.NewBoolVar(f'no_overlap_x_{i}_{j}')
        model.Add(x_coords[i] + sides[i] <= x_coords[j]).OnlyEnforceIf(no_overlap_x)
        model.Add(x_coords[i] + sides[i] > x_coords[j]).OnlyEnforceIf(no_overlap_x.Not())

        # square i is to the right of square j
        no_overlap_x2 = model.NewBoolVar(f'no_overlap_x2_{i}_{j}')
        model.Add(x_coords[j] + sides[j] <= x_coords[i]).OnlyEnforceIf(no_overlap_x2)
        model.Add(x_coords[j] + sides[j] > x_coords[i]).OnlyEnforceIf(no_overlap_x2.Not())

        # square i is below square j
        no_overlap_y = model.NewBoolVar(f'no_overlap_y_{i}_{j}')
        model.Add(y_coords[i] + sides[i] <= y_coords[j]).OnlyEnforceIf(no_overlap_y)
        model.Add(y_coords[i] + sides[i] > y_coords[j]).OnlyEnforceIf(no_overlap_y.Not())

        # square i is above square j
        no_overlap_y2 = model.NewBoolVar(f'no_overlap_y2_{i}_{j}')
        model.Add(y_coords[j] + sides[j] <= y_coords[i]).OnlyEnforceIf(no_overlap_y2)
        model.Add(y_coords[j] + sides[j] > y_coords[i]).OnlyEnforceIf(no_overlap_y2.Not())

        # At least one of these four conditions must hold to avoid overlap
        model.AddBoolOr([no_overlap_x, no_overlap_x2, no_overlap_y, no_overlap_y2])

# 3. The sum of the areas of the small squares equals the area of the big square
# (Given by problem statement, so no spare capacity)
# We do not need to add this as a constraint since input is consistent.

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x_coords': [solver.Value(x) for x in x_coords],
        'y_coords': [solver.Value(y) for y in y_coords]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")