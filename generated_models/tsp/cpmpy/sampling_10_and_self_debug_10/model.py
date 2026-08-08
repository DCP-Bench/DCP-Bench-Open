
import cpmpy as cp
import json
import numpy as np

# Data
locations = [
    (288, 149), (288, 129), (270, 133), (256, 141), (256, 163), (246, 157),
    (236, 169), (228, 169), (228, 148), (220, 164), (212, 172), (204, 159)
]
n = len(locations)

# Compute Euclidean distances scaled to integers (to avoid floats)
dist = np.zeros((n, n), dtype=int)
for i in range(n):
    for j in range(n):
        if i != j:
            dist[i, j] = int(np.hypot(locations[i][0]-locations[j][0], locations[i][1]-locations[j][1]))

# Model definition
model = cp.Model()

# Decision Variables
# x[i,j] = 1 if path goes from city i to city j, else 0
x = cp.boolvar(shape=(n, n), name="x")

# u[i] for subtour elimination (MTZ formulation)
u = cp.intvar(1, n, shape=n, name="u")

# Constraints

# No loops: x[i,i] = 0
for i in range(n):
    model += (x[i, i] == 0)

# Each city has exactly one outgoing edge
for i in range(n):
    model += (cp.sum(x[i, :]) == 1)

# Each city has exactly one incoming edge
for j in range(n):
    model += (cp.sum(x[:, j]) == 1)

# MTZ subtour elimination constraints (for i != 0 and j != 0)
for i in range(1, n):
    for j in range(1, n):
        if i != j:
            # u[i] - u[j] + n * x[i,j] <= n-1
            model += (u[i] - u[j] + n * x[i, j] <= n - 1)

# Objective: minimize total travel distance
travel_distance = cp.sum([dist[i, j] * x[i, j] for i in range(n) for j in range(n)])

model.minimize(travel_distance)

# Solve and print
if model.solve():
    solution = {'travel_distance': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
