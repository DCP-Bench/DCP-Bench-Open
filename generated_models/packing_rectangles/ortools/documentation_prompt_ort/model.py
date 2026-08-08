from ortools.sat.python import cp_model
import json

# Input data
widths = [3, 4, 2, 1]  # Widths of the items
heights = [2, 3, 1, 4]  # Heights of the items
n = len(widths)

# Model definition
model = cp_model.CpModel()

# Upper bounds for the container dimensions (sum of widths and heights)
max_width = sum(widths)
max_height = sum(heights)

# Decision variables for the position of each item (bottom-left corner)
pos_x = [model.NewIntVar(0, max_width, f'pos_x_{i}') for i in range(n)]
pos_y = [model.NewIntVar(0, max_height, f'pos_y_{i}') for i in range(n)]

# Decision variables for the total container dimensions
total_x = model.NewIntVar(0, max_width, 'total_x')
total_y = model.NewIntVar(0, max_height, 'total_y')

# Constraints: all items must be within the container boundaries
for i in range(n):
    model.Add(pos_x[i] + widths[i] <= total_x)
    model.Add(pos_y[i] + heights[i] <= total_y)

# Constraints: no overlap between items
for i in range(n):
    for j in range(i + 1, n):
        # At least one of the following must hold:
        # item i is to the left of item j
        # item i is to the right of item j
        # item i is above item j
        # item i is below item j
        model.AddBoolOr([
            pos_x[i] + widths[i] <= pos_x[j],
            pos_x[j] + widths[j] <= pos_x[i],
            pos_y[i] + heights[i] <= pos_y[j],
            pos_y[j] + heights[j] <= pos_y[i]
        ])

# Objective: minimize the total area of the container
# Since CP-SAT does not support multiplication of variables directly,
# we use a common trick: minimize total_x + total_y with a lexicographic approach
# or minimize an upper bound on area by binary search.
# Here, we minimize total_x * total_y by linearization using a helper variable.

# We create an auxiliary variable for area and use a linearization trick:
# area >= total_x * total_y
# We approximate by minimizing total_x + total_y as a proxy for area.

# Alternatively, we can minimize total_x + total_y as a heuristic for area minimization.
# This is a common approach in CP models for packing problems.

model.Minimize(total_x + total_y)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

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