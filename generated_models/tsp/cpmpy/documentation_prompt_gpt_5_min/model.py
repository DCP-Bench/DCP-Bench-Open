
import cpmpy as cp
import json
import math

# Data
locations = [
    (288, 149), (288, 129), (270, 133), (256, 141), (256, 163), (246, 157),
    (236, 169), (228, 169), (228, 148), (220, 164), (212, 172), (204, 159)
]
# End of data

n = len(locations)

# Precompute integer (rounded) Euclidean distances between cities
dist = [[0]*n for _ in range(n)]
for i in range(n):
    xi, yi = locations[i]
    for j in range(n):
        xj, yj = locations[j]
        d = math.hypot(xi - xj, yi - yj)
        dist[i][j] = int(round(d))

# Model definition
model = cp.Model()

# Decision Variables
# succ[i] is the successor city index after city i
succ = cp.intvar(0, n-1, shape=n, name="succ")

# Constraints
# Enforce that successors form a single Hamiltonian circuit visiting all nodes
model += cp.Circuit(succ)

# Objective: minimize total travel distance along the circuit
# Use Element to pick the distance for each arc i -> succ[i]
arc_costs = [cp.Element(dist[i], succ[i]) for i in range(n)]
total_cost = cp.sum(arc_costs)
model.minimize(total_cost)

# Solve and print
if model.solve():
    solution = {'travel_distance': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
