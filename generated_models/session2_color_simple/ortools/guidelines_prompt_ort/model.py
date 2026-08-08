
from ortools.sat.python import cp_model
import json

# Input data
graph = [  # the adjacency of the countries, (i, j) means that country i is adjacent to country j
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
# colors[i] is the color assigned to country i+1, using integers starting from 1
colors = [
    model.NewIntVar(1, num_countries, f'colors[{i}]') for i in range(num_countries)
]

# Variable to represent the maximum color used
max_color = model.NewIntVar(1, num_countries, 'max_color')

# Constraints
# 1. Adjacent countries cannot have the same color
for (i, j) in graph:
    # Adjust for zero-based indexing
    model.Add(colors[i - 1] != colors[j - 1])

# 2. Link max_color with actual colors: max_color >= each color
for i in range(num_countries):
    model.Add(colors[i] <= max_color)

# Objective: minimize the number of colors used
model.Minimize(max_color)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'colors': [solver.Value(colors[i]) for i in range(num_countries)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
