
import cpmpy as cp
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

# Model definition
model = cp.Model()

# Decision Variables: colors for each country (1-based to 6)
colors = cp.intvar(1, 6, shape=6, name="colors")

# Constraints: adjacent countries have different colors
for edge in graph:
    i, j = edge
    model += (colors[i-1] != colors[j-1])

# Objective: minimize the maximum color used
model.minimize(cp.max(colors))

# Solve and print
if model.solve():
    solution = {'colors': colors.value().tolist()}
    print(json.dumps(solution))
else:
    print("No solution found.")
