
import cpmpy as cp
import json

# Data
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
# End of data

# Model definition
model = cp.Model()

# There are 6 countries: indices 1..6
# Decision variables: colors for each country, domain 1..6
colors = cp.intvar(1, 6, shape=6, name="colors")

# Additional variable k: the maximum color used
k = cp.intvar(1, 6, name="k")

# Constraints
# 1) Adjacent countries must have different colors
for (i, j) in graph:
    # convert to 0-based indices
    model += colors[i-1] != colors[j-1]

# 2) Link k to the colors: all colors <= k
for i in range(6):
    model += colors[i] <= k

# Objective: minimize the number of colors (k)
model.minimize(k)

# Solve and print
if model.solve():
    solution = {
        'colors': colors.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
