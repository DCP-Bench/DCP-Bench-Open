from cpmpy import *
import json
import math

# Input data
locations = [
    (288, 149), (288, 129), (270, 133), (256, 141), (256, 163), (246, 157),
    (236, 169), (228, 169), (228, 148), (220, 164), (212, 172), (204, 159)
]

num_cities = len(locations)

# Decision variables
# tour[i] = j means that city j is the i-th city in the tour
tour = intvar(0, num_cities - 1, shape=num_cities, name="tour")

# Ensure all cities are visited exactly once
model = Model([
    AllDifferent(tour)
])

# Precompute all pairwise distances
num_cities = len(locations)
distances = [[0] * num_cities for _ in range(num_cities)]
for i in range(num_cities):
    for j in range(num_cities):
        dx = locations[i][0] - locations[j][0]
        dy = locations[i][1] - locations[j][1]
        distances[i][j] = (dx**2 + dy**2)**0.5

# Define the total travel distance using CPMPy Element constraints
travel_distance = 0
for i in range(num_cities):
    from_city = tour[i]
    to_city = tour[(i + 1) % num_cities]
    # Use Element to index into the distances matrix
    travel_distance += Element(distances, from_city, to_city)

model.minimize(travel_distance)

# Solve the model
model.solve()

# Print the solution
solution = {"travel_distance": travel_distance.value()}
print(json.dumps(solution))