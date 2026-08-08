from cpmpy import *
import json

# Input data
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

# Decision variables
# colors[i] is the color assigned to country i (0-indexed)
colors = intvar(1, num_countries, shape=num_countries, name="colors")

# Model
model = Model()

# Objective: minimize the number of colors used
model.minimize(max(colors))

# Constraints: adjacent countries must have different colors
for u, v in graph:
    model += [colors[u - 1] != colors[v - 1]]

# Solve the model
model.solve()

# Print the solution
solution = {"colors": colors.value().tolist()}
print(json.dumps(solution))