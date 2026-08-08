
import cpmpy as cp
import json

# Data
graph = [  # adjacency list as given, 1-based indices
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

# Decision Variables: colors for 6 countries, values start from 1 up to 6 (upper bound large enough)
colors = cp.intvar(1, 6, shape=6, name="colors")

# Constraints: neighboring countries cannot have the same colour
for (i, j) in graph:
    # convert 1-based to 0-based indices
    model += (colors[i - 1] != colors[j - 1])

# Objective: minimize the number of colours used.
# Minimize the maximum colour value used (labels start at 1, so this equals the count of colours after relabelling)
model.minimize(cp.Maximum(colors))

# Solve and print
if model.solve():
    solution = {'colors': colors.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
