
import cpmpy as cp
import json

# Data
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

model = cp.Model()

# Decision variables: colors for each country (1-based to 6)
colors = cp.intvar(1, 6, shape=6, name="colors")

# Constraints: adjacent countries have different colors
for i, j in graph:
    model += (colors[i-1] != colors[j-1])

# Objective: minimize the number of colors used (minimize the maximum color)
model.minimize(cp.Maximum(colors))

# Solve and print
if model.solve():
    solution = {'colors': colors.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
