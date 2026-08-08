# Import libraries
from cpmpy import *
import json
import numpy as np

# Parameters
locations = [
    (288, 149), (288, 129), (270, 133), (256, 141), (256, 163), (246, 157),
    (236, 169), (228, 169), (228, 148), (220, 164), (212, 172), (204, 159)
]
n = len(locations)

# Precompute distance matrix
dist_matrix = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        x1, y1 = locations[i]
        x2, y2 = locations[j]
        dist_matrix[i][j] = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

# Scale distances to integers (multiply by 100 and round)
scaled_dist_matrix = (dist_matrix * 100).astype(int)

# Decision Variables
next_city = intvar(0, n-1, shape=n, name="next_city")  # Next city in the tour
travel_distance = intvar(0, int(1e6), name="travel_distance")  # Total travel distance

# Model
model = Model()

# Constraint: Each city is visited exactly once (permutation)
model += AllDifferent(next_city)

# Constraint: No subtours (ensure single cycle)
model += circuit(next_city)

# Calculate total travel distance using scaled distances
model += travel_distance == sum([Element(scaled_dist_matrix[i,:], next_city[i]) for i in range(n)])

# Objective: minimize travel distance
model.minimize(travel_distance)

# Solve
model.solve()

# Print solution (convert back to original scale by dividing by 100)
solution = {
    "travel_distance": travel_distance.value() / 100
}
print(json.dumps(solution))
# End of CPMPy script