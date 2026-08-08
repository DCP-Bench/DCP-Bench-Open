
import cpmpy as cp
import json

# Input data
# Countries: Belgium(1), Denmark(2), France(3), Germany(4), Netherlands(5), Luxembourg(6)
# graph edges represented as pairs (i,j) of adjacent countries
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
n_countries = 6

# Model definition
model = cp.Model()

# Decision variables
# colors[i] = color assigned to country i+1, colors domain starts from 1 up to n_countries (worst case all different colors)
colors = cp.intvar(1, n_countries, shape=n_countries, name="colors")

# Auxiliary variable to minimize: max color used
max_color = cp.intvar(1, n_countries, name="max_color")

# Constraints
# 1. Adjacent countries have different colors
for (c1, c2) in graph:
    model += (colors[c1-1] != colors[c2-1])

# 2. max_color is at least the max of assigned colors
for i in range(n_countries):
    model += (colors[i] <= max_color)

# Objective: minimize the number of colors used
model.minimize(max_color)

# Solve and print
if model.solve():
    solution = {'colors': colors.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
