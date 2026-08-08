# Import libraries
from cpmpy import *
import json

# Parameters
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
n_countries = 6  # Belgium, Denmark, France, Germany, Netherlands, Luxembourg

# Decision Variables
colors = intvar(1, n_countries, shape=n_countries, name="colors")  # Colors assigned to each country

# Model
model = Model()

# Constraint: all adjacent countries must have different colors
for (i, j) in graph:
    model += colors[i-1] != colors[j-1]  # -1 because countries are numbered from 1

# Objective: minimize the maximum color used (which minimizes the number of colors)
max_color = max(colors)
model.minimize(max_color)

# Solve
model.solve()

# Print solution
solution = {
    "colors": colors.value().tolist()
}
print(json.dumps(solution))
# End of CPMPy script