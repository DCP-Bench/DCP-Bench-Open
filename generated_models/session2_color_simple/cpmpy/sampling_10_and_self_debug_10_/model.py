
import cpmpy as cp
import json

# Data
graph = [  # edges are 1-based indices of the 6 countries
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

# Model definition
model = cp.Model()

# Decision Variables
# colors[i] is the colour (integer starting from 1) assigned to country i (0-based internally)
colors = cp.intvar(1, 6, shape=6, name="colors")
# m is the maximum colour used; we minimize this to use as few colours as possible
m = cp.intvar(1, 6, name="m")

# Constraints
# Adjacent countries cannot have the same colour (convert 1-based input to 0-based indices)
for (i, j) in graph:
    model += (colors[i - 1] != colors[j - 1])

# m must be at least every assigned colour (so m = max(colors))
for k in range(6):
    model += (m >= colors[k])

# Symmetry breaking: assign the first country colour 1 (we can always relabel colours)
model += (colors[0] == 1)

# Objective: minimize the number of colours used (m)
model.minimize(m)

# Solve and print
if model.solve():
    solution = {'colors': colors.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
