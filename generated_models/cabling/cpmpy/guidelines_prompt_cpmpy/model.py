
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: positions of A, B, C, D, E, F, G, H in the rack (1..8)
# Index mapping: 0->A, 1->B, 2->C, 3->D, 4->E, 5->F, 6->G, 7->H
p = cp.intvar(1, 8, shape=8, name="p")

# All devices must occupy distinct 1U slots
model += [cp.AllDifferent(p)]

# Cable requirements: (device1_index, device2_index, number_of_cables)
edges = [
    (0, 7, 1),  # A-H
    (0, 4, 2),  # A-E
    (1, 5, 4),  # B-F
    (2, 6, 1),  # C-G
    (2, 3, 1),  # C-D
    (2, 4, 1),  # C-E
    (3, 7, 3),  # D-H
    (6, 7, 1)   # G-H
]

# Build weighted sum of cable lengths
dist_terms = []
for i, j, w in edges:
    # length = abs(position_i - position_j) * weight
    dist_terms.append(w * cp.abs(p[i] - p[j]))

total_length = cp.sum(dist_terms)

# Objective: minimize total cable length
model.minimize(total_length)

# Solve and print
if model.solve():
    solution = {'final_sum': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
