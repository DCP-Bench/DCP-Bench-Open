
import cpmpy as cp
import json

# Devices: A, B, C, D, E, F, G, H
# We place each device in a distinct 1..8 U position in the rack.
names = ["A","B","C","D","E","F","G","H"]
n = len(names)

# Model definition
model = cp.Model()

# Decision Variables: position of each device (1..8)
pos = cp.intvar(1, 8, shape=n, name="pos")

# All devices occupy distinct U positions
model += cp.AllDifferent(pos)

# Cable requirements (device indices are 0-based according to names list)
# Each tuple: (index_i, index_j, number_of_cables)
edges = [
    (0, 7, 1),  # A - H : 1 cable
    (0, 4, 2),  # A - E : 2 cables
    (1, 5, 4),  # B - F : 4 cables
    (2, 6, 1),  # C - G : 1 cable
    (2, 3, 1),  # C - D : 1 cable
    (2, 4, 1),  # C - E : 1 cable
    (3, 7, 3),  # D - H : 3 cables
    (6, 7, 1),  # G - H : 1 cable
]

# Sum of cable lengths: multiplicity * vertical distance (abs difference in U)
terms = []
for (i, j, mult) in edges:
    terms.append(mult * cp.Abs(pos[i] - pos[j]))

total_cable_length = cp.sum(terms)

# Objective: minimize total cable length
model.minimize(total_cable_length)

# Solve and print
if model.solve():
    solution = {'final_sum': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
