
import cpmpy as cp
import json
import numpy as np

# Data
locations = [
    (288, 149), (288, 129), (270, 133), (256, 141), (256, 163), (246, 157),
    (236, 169), (228, 169), (228, 148), (220, 164), (212, 172), (204, 159)
]
# End of data

# Precompute integer-rounded Euclidean distances
n = len(locations)
dist = np.zeros((n, n), dtype=int)
for i in range(n):
    xi, yi = locations[i]
    for j in range(n):
        xj, yj = locations[j]
        dx = xi - xj
        dy = yi - yj
        dist[i, j] = int(round((dx*dx + dy*dy) ** 0.5))

# Model definition
model = cp.Model()

# Decision Variables
succ = cp.intvar(0, n-1, shape=n, name="succ")

# Constraints
# Single Hamiltonian cycle visiting all nodes exactly once
model += cp.Circuit(succ)

# Objective: minimize total travel distance
arc_costs = [cp.Element(dist[i], succ[i]) for i in range(n)]
total_cost = cp.sum(arc_costs)
model.minimize(total_cost)

# Solve and print
if model.solve():
    solution = {'travel_distance': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
