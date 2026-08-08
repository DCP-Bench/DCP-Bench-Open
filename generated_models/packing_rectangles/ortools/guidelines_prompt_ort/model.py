
from ortools.sat.python import cp_model
import json

# Input data
widths = [3, 4, 2, 1]
heights = [2, 3, 1, 4]

# Create the CP model
model = cp_model.CpModel()
n = len(widths)
max_width = sum(widths)
max_height = sum(heights)

# Decision variables
pos_x = [
    model.NewIntVar(0, max_width - widths[i], f'pos_x[{i}]')
    for i in range(n)
]
pos_y = [
    model.NewIntVar(0, max_height - heights[i], f'pos_y[{i}]')
    for i in range(n)
]
total_x = model.NewIntVar(0, max_width, 'total_x')
total_y = model.NewIntVar(0, max_height, 'total_y')
area = model.NewIntVar(0, max_width * max_height, 'area')

# Constraints: each item must lie within the larger rectangle
for i in range(n):
    model.Add(pos_x[i] + widths[i] <= total_x)
    model.Add(pos_y[i] + heights[i] <= total_y)

# Non-overlap constraints for every pair of items
for i in range(n):
    for j in range(i + 1, n):
        # Four boolean indicators for separation in x or y
        b1 = model.NewBoolVar(f'b1_{i}_{j}')  # i right of j
        b2 = model.NewBoolVar(f'b2_{i}_{j}')  # j right of i
        b3 = model.NewBoolVar(f'b3_{i}_{j}')  # i above j
        b4 = model.NewBoolVar(f'b4_{i}_{j}')  # j above i

        # If b1 is true, i is to the right of j
        model.Add(pos_x[i] >= pos_x[j] + widths[j]).OnlyEnforceIf(b1)
        # If b2 is true, j is to the right of i
        model.Add(pos_x[j] >= pos_x[i] + widths[i]).OnlyEnforceIf(b2)
        # If b3 is true, i is above j
        model.Add(pos_y[i] >= pos_y[j] + heights[j]).OnlyEnforceIf(b3)
        # If b4 is true, j is above i
        model.Add(pos_y[j] >= pos_y[i] + heights[i]).OnlyEnforceIf(b4)

        # At least one separation must hold
        model.AddBoolOr([b1, b2, b3, b4])

# Link area = total_x * total_y
model.AddMultiplicationEquality(area, [total_x, total_y])

# Objective: minimize the total area
model.Minimize(area)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'pos_x': [solver.Value(pos_x[i]) for i in range(n)],
        'pos_y': [solver.Value(pos_y[i]) for i in range(n)],
        'total_x': solver.Value(total_x),
        'total_y': solver.Value(total_y)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
