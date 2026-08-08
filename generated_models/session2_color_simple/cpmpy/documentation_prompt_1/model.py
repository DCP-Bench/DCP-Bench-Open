
import cpmpy as cp
import json

# Data
# Countries: 1=Belgium, 2=Denmark, 3=France, 4=Germany, 5=Netherlands, 6=Luxembourg
graph = [  # adjacency pairs (i, j)
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
# End of data

model = cp.Model()

num_countries = 6
# Decision variables: color for each country (1-based)
colors = cp.intvar(1, num_countries, shape=num_countries, name="colors")

# Constraints: adjacent countries cannot have the same color
for (c1, c2) in graph:
    model += (colors[c1-1] != colors[c2-1])

# Objective: minimize the number of colors used
# We introduce an auxiliary variable max_color to represent the max color used
max_color = cp.intvar(1, num_countries, name="max_color")
model += (max_color == cp.Maximum(colors))
model.minimize(max_color)

if model.solve():
    solution = {'colors': colors.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
