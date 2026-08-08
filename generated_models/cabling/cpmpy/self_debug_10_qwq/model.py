
import cpmpy as cp
import json

# Define the positions for each device (A to H) as integer variables from 1 to 8
positions = cp.intvar(1, 8, shape=8, name="pos")

model = cp.Model()

# All devices must be placed in distinct positions
model += cp.AllDifferent(positions)

# List of connections with their counts (device indices, count)
connections = [
    (0, 7, 1),   # A <-> H (1 cable)
    (0, 4, 2),   # A <-> E (2 cables)
    (1, 5, 4),   # B <-> F (4 cables)
    (2, 6, 1),   # C <-> G (1 cable)
    (2, 3, 1),   # C <-> D (1 cable)
    (2, 4, 1),   # C <-> E (1 cable)
    (3, 7, 3),   # D <-> H (3 cables)
    (6, 7, 1)    # G <-> H (1 cable)
]

# Calculate the total cable length
terms = []
for i, j, count in connections:
    distance = cp.abs(positions[i] - positions[j])
    terms.append(count * distance)
total_cost = cp.sum(terms)

# Objective: minimize the total cable length
model.minimize(total_cost)

# Solve and print the result
if model.solve():
    solution = {'final_sum': int(model.objective_value())}
    print(json.dumps(solution))
else:
    print("No solution found.")
