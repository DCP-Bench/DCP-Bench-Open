
import cpmpy as cp
import json

# Data
# Countries: [Belgium, Denmark, France, Germany, Netherlands, Luxembourg] indexed as 1..6
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
n_countries = 6
# End of data

# Model definition
model = cp.Model()

# Decision Variables
colors = cp.intvar(1, n_countries, shape=n_countries, name="colors")  # color of each country
max_color = cp.intvar(1, n_countries, name="max_color")  # maximum color used

# Constraints
# Adjacent countries must have different colors
for (i, j) in graph:
    model += (colors[i-1] != colors[j-1])

# Link max_color to the maximum of assigned colors
model += (max_color == cp.Maximum(list(colors)))

# Objective: minimize the number of colors used (i.e., the maximum color index)
model.minimize(max_color)

# Solve and print
if model.solve():
    solution = {'colors': colors.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
