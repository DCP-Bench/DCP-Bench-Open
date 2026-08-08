from ortools.sat.python import cp_model
import json

# Input data
# Countries: Belgium(1), Denmark(2), France(3), Germany(4), Netherlands(5), Luxembourg(6)
# graph edges represent adjacency between countries by their indices
graph = [
    [3, 1],
    [3, 6],
    [3, 4],
    [6, 4],
    [6, 1],
    [1, 5],
    [1, 4],
    [4, 5],
    [4, 2]
]

# Number of countries
num_countries = 6

# Model definition
model = cp_model.CpModel()

# Decision Variables
# colors[i] is the color assigned to country i+1 (1-based indexing)
max_colors = num_countries  # upper bound on colors (worst case: all different)
colors = [model.NewIntVar(1, max_colors, f'color_{i+1}') for i in range(num_countries)]

# Constraints
# Adjacent countries must have different colors
for edge in graph:
    c1, c2 = edge
    # Adjust for zero-based indexing
    model.Add(colors[c1 - 1] != colors[c2 - 1])

# Auxiliary variable for the maximum color used
max_color_used = model.NewIntVar(1, max_colors, 'max_color_used')
model.AddMaxEquality(max_color_used, colors)

# Objective: minimize the number of colors used
model.Minimize(max_color_used)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'colors': [solver.Value(colors[i]) for i in range(num_countries)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")